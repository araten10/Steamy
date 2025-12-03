import asyncio
import logging
import platform
import random
import shutil
import sys
import tkinter as tk
from pathlib import Path
from threading import Thread
from tkinter import ttk
from typing import Callable

import aiohttp
import booru
import vdf


def get_steam_path() -> Path:
    # TODO: There can be other paths, maybe multiple?
    match platform.system():
        case "Linux":
            return Path("~/.local/share/Steam").expanduser()
        case "Windows":
            return Path("C:/Program Files (x86)/Steam")


def dirs_to_ids(parent: Path) -> list[str]:
    return [path.name for path in parent.iterdir() if path.is_dir()]


def get_game_ids() -> list[str]:
    return dirs_to_ids(get_steam_path() / "appcache" / "librarycache")


def get_user_ids() -> list[str]:
    return dirs_to_ids(get_steam_path() / "userdata")


def get_username_to_id() -> list[str]:
    steam_id3_list = get_user_ids()
    username_to_id = {}
    for steam_id3 in steam_id3_list:
        vdf_file = vdf.dumps(vdf.load(open(f"{get_steam_path()}/userdata/{steam_id3}/config/localconfig.vdf", encoding="utf8")))
        vdf_dict = vdf.loads(vdf_file)

        username_to_id[vdf_dict["UserLocalConfigStore"]["friends"]["PersonaName"]] = steam_id3
    return username_to_id


def get_grid_path(user_id: str) -> Path:
    return get_steam_path() / "userdata" / user_id / "config" / "grid"


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


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    root = tk.Tk()
    root.geometry("320x240")

    run_frame = tk.Frame(root)
    run_frame.pack(expand=1)

    user_select_frame = tk.Frame(run_frame)
    user_select_frame.pack()

    # For making sure that the "Select Steam Account" folder isn't accidentally created
    def enable_buttons(*_args) -> None:
        if user_var.get() != "Select Steam Account":
            pornify_button.config(state="normal")
            resteam_button.config(state="normal")

    # TODO: Get actual username corresponding to user id and display it here for ease of use
    user_var = tk.StringVar(root)
    user_var.trace("w", enable_buttons)
    username_to_id = get_username_to_id()

    user_selection_dropdown = ttk.Combobox(user_select_frame, state="readonly", textvariable=user_var, values=list(username_to_id.keys()))
    user_selection_dropdown.set("Select Steam Account")
    user_selection_dropdown.pack(pady=5)

    start_stop_frame = tk.Frame(run_frame)
    start_stop_frame.pack()

    pornify_progress_var = tk.IntVar()
    pornify_progressbar = ttk.Progressbar(run_frame, mode="determinate", maximum=len(get_game_ids()), variable=pornify_progress_var)
    pornify_button = ttk.Button(
        start_stop_frame,
        text="Pornify",
        command=lambda: Thread(target=lambda: asyncio.run(pornify(username_to_id[user_var.get()], pornify_progress_var))).start(),
    )
    pornify_button.grid(row=0, column=0, ipady=5)
    resteam_button = ttk.Button(start_stop_frame, text="Resteam", command=lambda: resteam(username_to_id[user_var.get()]))
    resteam_button.grid(row=0, column=1, ipady=5)
    # Initially disable buttons to wait for user to be properly selected
    pornify_button.config(state="disabled")
    resteam_button.config(state="disabled")
    pornify_progressbar.pack(pady=5, fill="x")

    root.mainloop()
