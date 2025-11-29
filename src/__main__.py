import platform
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import ttk


def pornify() -> None:
    # TODO: There can be other paths, maybe multiple?
    match platform.system():
        case "Linux":
            steam_path = Path("~/.local/share/Steam").expanduser()
        case "Windows":
            steam_path = Path("C:/Program Files (x86)/Steam")

    # TODO: There can be multiple users
    user_path = list((steam_path / "userdata").iterdir())[0]
    grid_path = user_path / "config" / "grid"
    grid_path.mkdir(parents=True, exist_ok=True)

    example = Path(__file__).parent.parent / "example.png"
    shutil.copyfile(example, grid_path / "4000_hero.png")

    print("Done")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("320x240")

    ttk.Button(root, text="Pornify", command=pornify).pack(pady=5, ipady=10, ipadx=5, expand=1)
    root.mainloop()
