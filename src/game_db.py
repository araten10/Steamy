import json
import logging
import random
from dataclasses import dataclass
from pathlib import Path
from time import sleep

import PyQt6.QtWidgets as QtW
import requests

from steam import Steam


@dataclass
class Game:
    name: str = ""
    danbooru: str = ""
    rule34: str = ""


def get_game_db() -> dict[str, Game]:
    game_db = {}
    path = Path(__file__).parent.parent / "game_database.json"

    if path.is_file():
        with open(path, "r") as f:
            game_db_json = json.load(f)

        for game_id, data in game_db_json["games"].items():
            game_db[game_id] = Game(**data)

    return game_db


def dump_game_library(steam: Steam, game_db: dict[str, Game]) -> None:
    dialog = QtW.QFileDialog()
    dialog.setWindowTitle("Dump Directory")
    dialog.setFileMode(QtW.QFileDialog.FileMode.Directory)
    dialog.exec()
    output = Path(dialog.selectedFiles()[0]) / "dumped_game_database.json"

    logging.info(f"There are {len(game_db)} games already in the database. These will be skipped if detected.")

    converted_dict = {}
    for game_id in steam.game_ids:
        if game_id in game_db:
            logging.info(f'Game ID {game_id} already found in database as "{game_db[game_id].name}". Skipping...')
            continue

        sleep(random.uniform(1.5, 2))  # Don't take this out! This is a rate limiter so Steam doesn't block requests.

        store_url = "https://store.steampowered.com/api/appdetails?appids=" + game_id
        body = requests.get(store_url).json()[game_id]
        if not body["success"]:
            logging.info(f"Failed retrieving name for ID {game_id}. Most likely a program and not a game, or removed from the steam store. Skipping...")
            continue

        name = body["data"]["name"]
        converted_dict[game_id] = {"name": name}
        logging.info(f"{name} added to dict. Total games: {len(converted_dict)}")

    with open(output, "w", encoding="utf8") as f:
        json.dump(converted_dict, f, indent=2, ensure_ascii=False)
