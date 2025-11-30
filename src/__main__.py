import asyncio
import platform
import random
import tkinter as tk
from tkinter import Frame
import urllib.request
from pathlib import Path
from tkinter import ttk
import booru

# TODO: There can be other paths, maybe multiple?
match platform.system():
    case "Linux":
        STEAM_PATH = Path("~/.local/share/Steam").expanduser()
    case "Windows":
        STEAM_PATH = Path("C:/Program Files (x86)/Steam")

USER_PATH_LIST = list((STEAM_PATH / "userdata").iterdir())

async def pornify(user: str) -> None:

    # TODO: There can be multiple users
    grid_path = STEAM_PATH / "userdata" / user / "config" / "grid"
    grid_path.mkdir(parents=True, exist_ok=True)

    dan = booru.Danbooru()
    res = await dan.search_image(query="order:rank")
    image = random.choice(booru.resolve(res))
    urllib.request.urlretrieve(image, grid_path / "4000_hero.png")

    print("Done Pornify")

async def resteam(user: str) -> None:

    # TODO: There can be multiple users
    grid_path = STEAM_PATH / "userdata" / user / "config" / "grid"
    grid_path.mkdir(parents=True, exist_ok=True)

    print("Done Resteam")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("320x240")

    # TODO: Get actual username corresponding to user id and display it here for ease of use
    usernames = []
    for user_path in USER_PATH_LIST:
        usernames.append(user_path.name)

    run_frame = Frame(root)
    run_frame.pack(expand=1)

    user_select_frame = Frame(run_frame)
    user_select_frame.pack()
    user_selection_dropdown = ttk.Combobox(user_select_frame, state="readonly", values=usernames)
    user_selection_dropdown.set("Select Steam Account")
    user_selection_dropdown.pack(pady=5)
    start_stop_frame = Frame(run_frame)
    start_stop_frame.pack()
    ttk.Button(start_stop_frame, text="Pornify", command=lambda: asyncio.run(pornify(user_selection_dropdown.get()))).grid(row=0, column=0, ipady=5)
    ttk.Button(start_stop_frame, text="Resteam", command=lambda: asyncio.run(resteam(user_selection_dropdown.get()))).grid(row=0, column=1, ipady=5)

    root.mainloop()
