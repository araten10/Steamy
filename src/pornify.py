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

from game_db import Game
from steam import Art, Grid, Steam

NO_RESULTS_ERROR = "no results, make sure you spelled everything right"


class PornifyThread(QThread):
    progress = pyqtSignal()
    done = pyqtSignal()

    def __init__(self, steam: Steam, game_db: dict[str, Game], username: str) -> None:
        super().__init__()

        self.game_db = game_db
        self.game_ids = steam.game_ids
        self.grid = Grid(steam, username)
        self.dan = booru.Danbooru()

        self.should_run = True

        if self.grid.path.exists():
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

    async def pornify(self) -> None:
        self.grid.path.mkdir(parents=True, exist_ok=True)
        self.grid.porn_flag.touch(exist_ok=True)

        async with aiohttp.ClientSession() as session:
            queue = self.game_ids
            while len(queue) > 0:
                tasks = [asyncio.create_task(self.pornify_game(session, game_id)) for game_id in queue[0:10]]
                del queue[0:10]
                await asyncio.gather(*tasks)
                await asyncio.sleep(1)

        logging.info("Pornify done")

    async def pornify_game(self, session: aiohttp.ClientSession, game_id: str) -> None:
        game = self.game_db.get(game_id, Game())
        posts = await self.search_booru(game)
        if len(posts) >= 3:
            await self.download_images(session, game_id, posts)
        else:
            logging.warning(f"Not enough results for query {game.danbooru}, got {len(posts)} but expected at least 3")

        self.progress.emit()

    async def search_booru(self, game: Game) -> list:
        while True:
            try:
                res = await self.dan.search(query=game.danbooru)
                return list(filter(lambda post: post["file_ext"] in ["png", "jpg", "jpeg"], booru.resolve(res)))
            except (ClientError, JSONDecodeError) as e:
                logging.warning(f"Booru search failed with {type(e).__name__}: {e}, retrying...")
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                if NO_RESULTS_ERROR in e.args:
                    return []  # No results from booru
                else:
                    raise e  # Unexpected error

    async def download_images(self, session: aiohttp.ClientSession, game_id: str, posts: list) -> None:
        assert len(posts) >= 3

        for art in [
            Art("Cover", "p", 600, 900, sample=True),
            Art("Background", "_hero", 3840, 1240, sample=False),
            Art("Wide Cover", "", 920, 430, sample=True),
        ]:
            # TODO: What if no post is a good enough match?
            scores = [(post, art.score(post["image_width"], post["image_height"])) for post in posts]
            post, _ = min(scores, key=lambda scored: scored[1])
            posts.remove(post)  # No duplicates

            # Samples (large_file_url) are always 850 wide
            url = post["large_file_url"] if art.sample else post["file_url"]
            while True:
                try:
                    async with session.get(url) as image_res:
                        with open(self.grid.path / f"{game_id}{art.suffix}.png", "wb") as f:
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
