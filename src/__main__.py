import platform
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import ttk

# TODO: There can be other paths, maybe multiple?
match platform.system():
    case "Linux":
        STEAM_PATH = Path("~/.local/share/Steam").expanduser()
    case "Windows":
        STEAM_PATH = Path("C:/Program Files (x86)/Steam")

USER_PATH_LIST = list((STEAM_PATH / "userdata").iterdir())

def pornify(user: str) -> None:

    # TODO: There can be multiple users
    grid_path = STEAM_PATH / "userdata" / user / "config" / "grid"
    grid_path.mkdir(parents=True, exist_ok=True)

    example = Path(__file__).parent.parent / "example.png"
    shutil.copyfile(example, grid_path / "4000_hero.png")

    print("Done")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("320x240")

    usernames = []
    for user_path in USER_PATH_LIST:
        usernames.append(user_path.name)

    user_selection_dropdown = ttk.Combobox(root, state="readonly", values=usernames)
    user_selection_dropdown.set("Select Steam Account")
    user_selection_dropdown.pack(pady=5, expand=1)
    ttk.Button(root, text="Pornify", command=pornify(user_selection_dropdown.get())).pack(pady=5, ipady=10, ipadx=5, expand=1)
    root.mainloop()
