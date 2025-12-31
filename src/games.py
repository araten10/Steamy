import json
import logging
import random
from dataclasses import dataclass
from pathlib import Path
from time import sleep

import PyQt6.QtWidgets as QtW
import requests
from PyQt6.QtCore import QSize, QThread, pyqtSignal
from voluptuous import ALLOW_EXTRA, Number, Optional, Schema

import resources
from steam import Steam
from utils import load_json


@dataclass
class Game:
    id: str
    name: str = ""
    danbooru: str | None = None
    rule34: str | None = None
    e621: str | None = None
    ignore: bool | None = None


def get_game_db() -> dict[str, Game]:
    schema = Schema(
        {
            "games": {
                Number(scale=0): {
                    "name": str,
                    Optional("danbooru"): str,
                    Optional("rule34"): str,
                    Optional("e621"): str,
                    Optional("ignore"): bool,
                }
            }
        },
        required=True,
        extra=ALLOW_EXTRA,
    )

    game_db_json = load_json(resources.GAME_DATABASE, schema) or {"games": {}}
    game_db = {game_id: Game(game_id, **data) for game_id, data in game_db_json["games"].items()}
    return game_db


def search_games(search_term: str, cc: str) -> None:
    # Search params: ?term=: search term, &l=english: language, &cc=: country code
    search_url = "https://store.steampowered.com/api/storesearch/?term=" + search_term + "&l=english&cc=" + cc
    result = requests.get(search_url).json()
    games = {game["id"]: {"name": game["name"]} for game in result["items"]}

    dialog = QtW.QDialog()
    dialog.resize(QSize(350, 500))

    layout = QtW.QVBoxLayout()
    text = QtW.QTextEdit()
    text.setPlainText(json.dumps(games, indent=2, ensure_ascii=False))

    layout.addWidget(text)
    dialog.setLayout(layout)
    dialog.exec()


class LibraryDumperThread(QThread):
    progress = pyqtSignal()
    done = pyqtSignal(Path)

    def __init__(self, steam: Steam, game_db: dict[str, Game]) -> None:
        super().__init__()

        self.steam = steam
        self.game_db = game_db

        dialog = QtW.QFileDialog()
        dialog.setWindowTitle("Dump Directory")
        dialog.setFileMode(QtW.QFileDialog.FileMode.Directory)
        dialog.exec()

        self.output_dir = Path(dialog.selectedFiles()[0]) / "dumped_game_database.json"
        self.dump = {}

    def run(self) -> None:
        logging.info(f"There are {len(self.game_db)} games already in the database. These will be skipped if detected.")

        checkpoint = 10
        for index, game_id in enumerate(self.steam.game_ids):
            self.find_name(game_id)
            self.progress.emit()

            if (index + 1) % checkpoint == 0:
                self.write_dump()  # Write a checkpoint every so often in case something goes wrong

            sleep(random.uniform(1.5, 2))  # Don't take this out! This is a rate limiter so Steam doesn't block requests.

        self.write_dump()
        self.done.emit(self.output_dir)
        logging.info("Dump done")

    def find_name(self, game_id: str) -> None:
        if game_id in self.game_db:
            logging.info(f'Game ID {game_id} already found in database as "{self.game_db[game_id].name}". Skipping...')
            return

        store_url = "https://store.steampowered.com/api/appdetails?appids=" + game_id
        body = requests.get(store_url).json()[game_id]
        if not body["success"]:
            logging.info(f"Failed retrieving name for ID {game_id}. Most likely a program and not a game, or removed from the steam store. Skipping...")
            return

        name = body["data"]["name"]
        self.dump[game_id] = {"name": name}
        logging.info(f"{name} added to dump. Total games: {len(self.dump)}")

    def write_dump(self) -> None:
        with open(self.output_dir, "w", encoding="utf8") as f:
            json.dump(self.dump, f, indent=2, ensure_ascii=False)
