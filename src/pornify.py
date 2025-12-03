import asyncio
import logging
import random
import shutil
import tkinter as tk
from pathlib import Path
from typing import Callable

import aiohttp
import booru

from steam import get_game_ids, get_grid_path


async def pornify_game(
    dan: booru.Danbooru, session: aiohttp.ClientSession, grid_path: Path, game_id: str, max_sleep: float, update_progress: Callable[[str], None]
) -> None:
    await asyncio.sleep(random.uniform(0, max_sleep))  # Wait a random amount to preemptively avoid rate limit

    while True:
        try:
            search_res = await dan.search(query="order:rank")
            posts = booru.resolve(search_res)
            break
        except Exception as e:
            logging.warning(f"Booru search failed with {type(e).__name__}: {e}, retrying...")
            await asyncio.sleep(random.uniform(1, 2))

    for art_suffix in ["", "p", "_hero"]:
        post = random.choice(posts)
        while True:
            try:
                async with session.get(post["large_file_url"]) as image_res:
                    with open(grid_path / f"{game_id}{art_suffix}.png", "wb") as f:
                        f.write(await image_res.read())
                    break
            except Exception as e:
                logging.warning(f"Image download failed with {type(e).__name__}: {e}, retrying...")
                await asyncio.sleep(random.uniform(1, 2))

    update_progress(game_id)


async def pornify(user_id: str, progress_var: tk.IntVar) -> None:
    grid_path = get_grid_path(user_id)
    grid_path.mkdir(parents=True, exist_ok=True)
    game_ids = get_game_ids()

    progress_var.set(0)
    games_done = {game_id: False for game_id in game_ids}

    def update_progress(game_id: str) -> None:
        games_done[game_id] = True
        progress = 0
        for done in games_done.values():
            if done:
                progress += 1
        progress_var.set(progress)

    async with aiohttp.ClientSession() as session:
        dan = booru.Danbooru()
        max_sleep = float(len(game_ids)) / 10
        tasks = [asyncio.create_task(pornify_game(dan, session, grid_path, game_id, max_sleep, update_progress)) for game_id in game_ids]
        await asyncio.gather(*tasks)

    logging.info("Pornify done")


def resteam(user_id: str) -> None:
    grid_path = get_grid_path(user_id)
    if grid_path.exists():
        shutil.rmtree(grid_path)

    # TODO: Find a more productive way to resteam without deleting all the porn you just downloaded, then add progressbar to it
    logging.info("Resteam done")
