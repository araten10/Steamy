import asyncio
import logging
import random
import shutil
import tkinter as tk
from json.decoder import JSONDecodeError
from pathlib import Path

import aiohttp
import booru
from aiohttp.client_exceptions import ClientError

from steam import Art, Steam


async def pornify_game(
    dan: booru.Danbooru, session: aiohttp.ClientSession, grid_path: Path, game_id: str, max_sleep: float, progress_var: tk.IntVar, progress_lock: asyncio.Lock
) -> None:
    await asyncio.sleep(random.uniform(0, max_sleep))  # Wait a random amount to preemptively avoid rate limit

    while True:
        try:
            search_res = await dan.search(query="order:rank")
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
                async with session.get(post["file_url"]) as image_res:  # TODO: Choose the best variant?
                    with open(grid_path / f"{game_id}{art.suffix}.png", "wb") as f:
                        f.write(await image_res.read())
                    break
            except ClientError as e:
                logging.warning(f"Image download failed with {type(e).__name__}: {e}, retrying...")
                await asyncio.sleep(random.uniform(1, 2))

    async with progress_lock:
        progress_var.set(progress_var.get() + 1)


async def pornify(steam: Steam, username: str, progress_var: tk.IntVar) -> None:
    grid_path = steam.get_grid_path(username)
    grid_path.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        dan = booru.Danbooru()
        max_sleep = float(len(steam.game_ids)) / 10
        progress_lock = asyncio.Lock()

        tasks = [asyncio.create_task(pornify_game(dan, session, grid_path, game_id, max_sleep, progress_var, progress_lock)) for game_id in steam.game_ids]
        await asyncio.gather(*tasks)

    logging.info("Pornify done")


def resteam(steam: Steam, username: str) -> None:
    grid_path = steam.get_grid_path(username)
    if grid_path.exists():
        shutil.rmtree(grid_path)

    # TODO: Find a more productive way to resteam without deleting all the porn you just downloaded, then add progressbar to it
    logging.info("Resteam done")
