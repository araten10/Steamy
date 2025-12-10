import asyncio
import json
import logging
import os
import random
import shutil
from json.decoder import JSONDecodeError

import aiohttp
import booru
import PyQt6.QtWidgets as QtW
from aiohttp.client_exceptions import ClientError
from PyQt6.QtCore import QThread, pyqtSignal

from steam import Art, Grid, Steam


class PornifyThread(QThread):
    progress = pyqtSignal()
    done = pyqtSignal()

    def __init__(self, steam: Steam, username: str) -> None:
        super().__init__()

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
        game_list = {}

        if os.path.isfile("game_list.json"):
            with open("game_list.json", "r", encoding="utf8") as f:
                game_list = json.load(f)

        self.grid.path.mkdir(parents=True, exist_ok=True)
        self.grid.porn_flag.touch(exist_ok=True)

        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(self.pornify_game(session, index, game_id, game_list)) for index, game_id in enumerate(self.game_ids)]
            await asyncio.gather(*tasks)

        logging.info("Pornify done")

    async def pornify_game(self, session: aiohttp.ClientSession, index: int, game_id: str, game_list: dict) -> None:
        await asyncio.sleep(random.uniform(0, float(index) / 10))  # Wait according to index to preemptively avoid rate limit

        while True:
            try:
                if game_id in game_list.keys():
                    print(f"ID {game_id} found in game list with tags {game_list[game_id]}")
                search_res = await self.dan.search(query="order:rank")
                posts = list(filter(lambda post: post["file_ext"] in ["png", "jpg", "jpeg"], booru.resolve(search_res)))
                break
            except (ClientError, JSONDecodeError) as e:
                logging.warning(f"Booru search failed with {type(e).__name__}: {e}, retrying...")
                await asyncio.sleep(random.uniform(1, 2))

        for art in [
            Art("Cover", "p", 600, 900),
            Art("Background", "_hero", 3840, 1240),
            Art("Wide Cover", "", 920, 430),
        ]:
            scores = [(post, art.score(post["image_width"], post["image_height"])) for post in posts]
            post, _ = min(scores, key=lambda scored: scored[1])
            posts.remove(post)  # No duplicates

            while True:
                try:
                    async with session.get(post["large_file_url"]) as image_res:  # TODO: Choose the best variant?
                        with open(self.grid.path / f"{game_id}{art.suffix}.png", "wb") as f:
                            f.write(await image_res.read())
                        break
                except ClientError as e:
                    logging.warning(f"Image download failed with {type(e).__name__}: {e}, retrying...")
                    await asyncio.sleep(random.uniform(1, 2))

        self.progress.emit()  # TODO: Is an asyncio.Lock necessary?


def resteam(steam: Steam, username: str) -> None:
    grid = Grid(steam, username)

    if grid.porn_flag.is_file():
        proceed = grid.make_backup()
        if not proceed:
            return
        grid.restore_backup(grid.custom_backup_path)

    logging.info("Resteam done")
