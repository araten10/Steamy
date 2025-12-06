import asyncio
import logging
import random
import shutil
from json.decoder import JSONDecodeError

import aiohttp
import booru
from aiohttp.client_exceptions import ClientError
from PyQt6.QtCore import QThread, pyqtSignal

from steam import Art, Steam


class PornifyThread(QThread):
    progress = pyqtSignal()
    done = pyqtSignal()

    def __init__(self, steam: Steam, username: str) -> None:
        super().__init__()

        self.game_ids = steam.game_ids
        self.grid_path = steam.get_grid_path(username)
        self.dan = booru.Danbooru()

    def run(self) -> None:
        asyncio.run(self.pornify())
        self.done.emit()

    async def pornify(self) -> None:
        self.grid_path.mkdir(parents=True, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(self.pornify_game(session, game_id)) for game_id in self.game_ids]
            await asyncio.gather(*tasks)

        logging.info("Pornify done")

    async def pornify_game(self, session: aiohttp.ClientSession, game_id: str) -> None:
        await asyncio.sleep(random.uniform(0, float(len(self.game_ids)) / 10))  # Wait a random amount to preemptively avoid rate limit

        while True:
            try:
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
                        with open(self.grid_path / f"{game_id}{art.suffix}.png", "wb") as f:
                            f.write(await image_res.read())
                        break
                except ClientError as e:
                    logging.warning(f"Image download failed with {type(e).__name__}: {e}, retrying...")
                    await asyncio.sleep(random.uniform(1, 2))

        self.progress.emit()  # TODO: Is an asyncio.Lock necessary?


def resteam(steam: Steam, username: str) -> None:
    grid_path = steam.get_grid_path(username)
    if grid_path.exists():
        shutil.rmtree(grid_path)

    # TODO: Find a more productive way to resteam without deleting all the porn you just downloaded, then add progressbar to it
    logging.info("Resteam done")
