import asyncio
import platform
import random
import shutil
import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import ttk

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


async def pornify(user_id: str, progress: ttk.Progressbar) -> None:
    grid_path = get_grid_path(user_id)
    grid_path.mkdir(parents=True, exist_ok=True)

    # Progress bar stuff
    grid_length = len(get_game_ids())
    grid_progress = tk.IntVar()
    progress.config(maximum=grid_length + 1, variable=grid_progress)

    dan = booru.Danbooru()

    for game_id in get_game_ids():
        res = await dan.search(query="order:rank", limit=3)
        posts = booru.resolve(res)
        for art_suffix in ["", "p", "_hero"]:
            post = random.choice(posts)
            urllib.request.urlretrieve(post["media_asset"]["variants"][0]["url"], grid_path / f"{game_id}{art_suffix}.png")
        grid_progress.set(grid_progress.get() + 1)
        print(f"{grid_progress.get()}/{grid_length}")

    print("Done Pornify")


def resteam(user_id: str) -> None:
    grid_path = get_grid_path(user_id)
    if grid_path.exists():
        shutil.rmtree(grid_path)

    # TODO: Find a more productive way to resteam without deleting all the porn you just downloaded, then add progressbar to it
    print("Done Resteam")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("320x240")

    run_frame = tk.Frame(root)
    run_frame.pack(expand=1)

    user_select_frame = tk.Frame(run_frame)
    user_select_frame.pack()

    porn_progress = ttk.Progressbar(run_frame, mode="determinate")

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
    pornify_button = ttk.Button(start_stop_frame, text="Pornify", command=lambda: asyncio.run(pornify(username_to_id[user_var.get()], porn_progress)))
    pornify_button.grid(row=0, column=0, ipady=5)
    resteam_button = ttk.Button(start_stop_frame, text="Resteam", command=lambda: resteam(username_to_id[user_var.get()]))
    resteam_button.grid(row=0, column=1, ipady=5)
    # Initially disable buttons to wait for user to be properly selected
    pornify_button.config(state="disabled")
    resteam_button.config(state="disabled")

    porn_progress.pack(pady=5, fill="x")

    root.mainloop()
