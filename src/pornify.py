import asyncio
import logging
import random
import shutil
from json.decoder import JSONDecodeError

import aiohttp
import booru
import PyQt6.QtWidgets as QtW
from aiohttp.client_exceptions import ClientError
from PyQt6.QtCore import QThread, pyqtSignal

from boorus import get_booru
from config import Config
from games import Game
from steam import Art, Grid, Steam
from utils import get_nested

NO_RESULTS_ERROR = "no results, make sure you spelled everything right"


class PornifyThread(QThread):
    progress = pyqtSignal()
    done = pyqtSignal()

    def __init__(self, config: Config, steam: Steam, game_db: dict[str, Game], username: str) -> None:
        super().__init__()

        self.game_db = game_db
        self.grid = Grid(steam, username)
        self.booru = asyncio.run(get_booru(config))
        self.concurrent_downloads = config.concurrent_downloads

        self.search_queue: list[Game] = [self.game_db.get(game_id, Game(game_id)) for game_id in steam.game_ids]
        self.search_lock = asyncio.Lock()
        self.search_done = False

        self.download_queue: list[Game, list] = []
        self.download_lock = asyncio.Lock()
        self.download_start = asyncio.Event()

        self.should_run = bool(self.booru)

        if self.should_run and self.grid.path.exists():
            if self.grid.porn_flag.is_file():
                message = QtW.QMessageBox()
                message.setIcon(QtW.QMessageBox.Icon.Question)
                message.setText("Already Pornified")
                message.setInformativeText("You are currently already using porn art. Do you want to redownload new porn?")

                message.setStandardButtons(QtW.QMessageBox.StandardButton.Yes | QtW.QMessageBox.StandardButton.No)
                self.should_run = message.exec() == QtW.QMessageBox.StandardButton.Yes
            else:
                self.should_run = self.grid.make_backup()

        if self.should_run and self.grid.porn_backup_path.exists():
            message = QtW.QMessageBox()
            message.setIcon(QtW.QMessageBox.Icon.Question)
            message.setText("Porn Art Backup Exists")
            message.setInformativeText("A porn art backup exists. Do you want to restore the backup or download new porn and delete the old backup?")

            restore = message.addButton("Restore backup", QtW.QMessageBox.ButtonRole.ApplyRole)
            download = message.addButton("Download and delete backup", QtW.QMessageBox.ButtonRole.DestructiveRole)
            message.addButton(QtW.QMessageBox.StandardButton.Cancel)
            message.exec()

            if message.clickedButton() == restore:
                self.grid.restore_backup(self.grid.porn_backup_path)
                self.should_run = False
            elif message.clickedButton() == download:
                shutil.rmtree(self.grid.porn_backup_path)
            else:
                self.should_run = False

    def run(self) -> None:
        if self.should_run:
            asyncio.run(self.pornify())

        self.done.emit()
        logging.info("Pornify done")

    async def pornify(self) -> None:
        self.grid.path.mkdir(parents=True, exist_ok=True)
        self.grid.porn_flag.touch(exist_ok=True)
        await asyncio.gather(
            asyncio.create_task(self.handle_search()),
            asyncio.create_task(self.handle_download()),
        )

    async def handle_search(self) -> None:
        tasks = []
        task_lock = asyncio.Lock()

        async def callback(task: asyncio.Task, game: Game) -> None:
            async with task_lock:
                tasks.remove(task)

            posts = task.result()
            if posts is None:
                async with self.search_lock:
                    self.search_queue.append(game)
            elif len(posts) > 3:
                async with self.download_lock:
                    self.download_queue.append((game, posts))
                    self.download_start.set()
            else:
                logging.warning(f"Not enough results for query {game.danbooru}, got {len(posts)} but expected at least 3")

        while len(tasks) > 0 or len(self.search_queue) > 0:
            while len(self.search_queue) > 0:
                async with self.search_lock:
                    game = self.search_queue.pop(0)
                task = asyncio.create_task(self.search_booru(game))

                async with task_lock:
                    tasks.append(task)
                task.add_done_callback(lambda t: asyncio.create_task(callback(t, game)))

                # Chance to be slightly slower than required to be on the safe side
                await asyncio.sleep(random.uniform(self.booru.rate_limit, self.booru.rate_limit * 1.25))

            if tasks:
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        self.search_done = True
        logging.info("Booru searches done")

    async def handle_download(self) -> None:
        tasks = []
        task_lock = asyncio.Lock()

        async def callback(task: asyncio.Task) -> None:
            async with task_lock:
                tasks.remove(task)
            self.progress.emit()

        await self.download_start.wait()
        while len(tasks) > 0 or len(self.download_queue) > 0 or not self.search_done:
            while len(tasks) < self.concurrent_downloads and len(self.download_queue) > 0:
                async with self.download_lock:
                    game, posts = self.download_queue.pop(0)
                task = asyncio.create_task(self.download_images(game, posts))

                async with task_lock:
                    tasks.append(task)
                task.add_done_callback(lambda t: asyncio.create_task(callback(t)))

            if tasks:
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            else:
                await asyncio.sleep(self.booru.rate_limit)  # No download tasks ready, wait for more booru results

        logging.info("Image downloads done")

    async def search_booru(self, game: Game) -> list | None:
        logging.debug(f"Searching {game}")

        try:
            res = await self.booru.search(game)
            return self.booru.filter(booru.resolve(res))
        except (ClientError, JSONDecodeError) as e:
            logging.warning(f"Booru search failed with {type(e).__name__}: {e}, requeueing...")
            return None
        except Exception as e:
            if NO_RESULTS_ERROR in e.args:
                return []  # No results from booru
            else:
                raise e  # Unexpected error

    async def download_images(self, game: Game, posts: list) -> None:
        logging.debug(f"Downloading {game}")

        # Samples should always be 850 wide
        for art in [
            Art("Cover", "p", 600, 900, sample=True),
            Art("Background", "_hero", 3840, 1240, sample=False),
            Art("Wide Cover", "", 920, 430, sample=True),
        ]:
            scores = [(post, art.score(get_nested(post, self.booru.width), get_nested(post, self.booru.height))) for post in posts]
            post, _ = min(scores, key=lambda scored: scored[1])
            posts.remove(post)  # No duplicates

            url = None
            if art.sample:
                url = get_nested(post, self.booru.sample_url)

            # Sample URL can be null on e621
            if not url:
                url = get_nested(post, self.booru.file_url)

            while True:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as image_res:
                            with open(self.grid.path / f"{game.id}{art.suffix}.png", "wb") as f:
                                f.write(await image_res.read())
                            break
                except ClientError as e:
                    logging.warning(f"Image download failed with {type(e).__name__}: {e}, retrying...")
                    await asyncio.sleep(random.uniform(1, 2))


def resteam(steam: Steam, username: str) -> None:
    grid = Grid(steam, username)

    if grid.porn_flag.is_file():
        proceed = grid.make_backup()
        if not proceed:
            return
        grid.restore_backup(grid.custom_backup_path)

    logging.info("Resteam done")
