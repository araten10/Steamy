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
#for scraping if we end up using that
#import requests
#from bs4 import BeautifulSoup

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

def convert_user_ids() -> list[str]:
    steamID3_list = get_user_ids()
    converted_dict = {}
    for steamID3 in steamID3_list:
        # The steam ID3 format is [U:1:<steamid>], we need to add the extra stuff
        completeID3 = "[U:1:" + steamID3 + "]"


        vdf_file = vdf.dumps(vdf.load(open(f"{get_steam_path()}/userdata/{steamID3}/config/localconfig.vdf", encoding="utf8")))
        vdf_dict = vdf.loads(vdf_file)

        converted_dict[vdf_dict['UserLocalConfigStore']['friends']['PersonaName']] = steamID3
    return converted_dict

def get_grid_path(user_id: str) -> Path:
    return get_steam_path() / "userdata" / user_id / "config" / "grid"


async def pornify(user_id: str) -> None:
    grid_path = get_grid_path(user_id)
    grid_path.mkdir(parents=True, exist_ok=True)

    dan = booru.Danbooru()
    res = await dan.search_image(query="order:rank")
    image = random.choice(booru.resolve(res))
    urllib.request.urlretrieve(image, grid_path / "image.png")

    for game_id in get_game_ids():
        for art_suffix in ["", "p", "_hero"]:
            shutil.copyfile(grid_path / "image.png", grid_path / f"{game_id}{art_suffix}.png")

    print("Done Pornify")


def resteam(user_id: str) -> None:
    grid_path = get_grid_path(user_id)
    if grid_path.exists():
        shutil.rmtree(grid_path)
    print("Done Resteam")


if __name__ == "__main__":
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
    user_dict = convert_user_ids()

    user_selection_dropdown = ttk.Combobox(user_select_frame, state="readonly", textvariable=user_var, values=list(user_dict.keys()))
    user_selection_dropdown.set("Select Steam Account")
    user_selection_dropdown.pack(pady=5)

    start_stop_frame = tk.Frame(run_frame)
    start_stop_frame.pack()
    pornify_button = ttk.Button(start_stop_frame, text="Pornify", command=lambda: asyncio.run(pornify(user_dict[user_var.get()])))
    pornify_button.grid(row=0, column=0, ipady=5)
    resteam_button = ttk.Button(start_stop_frame, text="Resteam", command=lambda: resteam(user_dict[user_var.get()]))
    resteam_button.grid(row=0, column=1, ipady=5)
    # Initially disable buttons to wait for user to be properly selected
    pornify_button.config(state="disabled")
    resteam_button.config(state="disabled")

    root.mainloop()
