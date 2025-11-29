import asyncio
import platform
import random
import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import ttk

import booru


async def pornify() -> None:
    # TODO: There can be other paths, maybe multiple?
    match platform.system():
        case "Linux":
            steam_path = Path("~/.local/share/Steam").expanduser()
        case "Windows":
            steam_path = Path()

    # TODO: There can be multiple users
    user_path = list((steam_path / "userdata").iterdir())[0]
    grid_path = user_path / "config" / "grid"
    grid_path.mkdir(parents=True, exist_ok=True)

    dan = booru.Danbooru()
    res = await dan.search_image(query="order:rank")
    image = random.choice(booru.resolve(res))
    urllib.request.urlretrieve(image, grid_path / "4000_hero.png")

    print("Done")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("320x240")

    ttk.Button(root, text="Pornify", command=lambda: asyncio.run(pornify())).pack(pady=5, ipady=10, ipadx=5, expand=1)
    root.mainloop()
