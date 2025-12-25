import json
import logging
from pathlib import Path

from voluptuous import ALLOW_EXTRA, All, Any, Range, Schema

from utils import load_json


class Config:
    def __init__(self) -> None:
        self.path = Path(__file__).parent.parent / "resources" / "config.json"

        self.supported_boorus = ["danbooru", "rule34", "e621"]
        self.schema = Schema(
            {
                "default_booru": Any(*self.supported_boorus),
                "concurrent_downloads": All(int, Range(min=1)),
                "rule34": {
                    "api_key": Any(str, None),
                    "user_id": Any(int, None),
                },
                "e621": {
                    "api_key": Any(str, None),
                    "user_id": Any(int, None),
                },
            },
            required=True,
            extra=ALLOW_EXTRA,
        )

        self.raw = {
            "default_booru": "danbooru",
            "concurrent_downloads": 10,
            "rule34": {
                "api_key": None,
                "user_id": None,
            },
            "e621": {
                "api_key": None,
                "user_id": None,
            },
        }

        self.load_fresh()

    def load(self) -> None:
        self.default_booru = self.raw["default_booru"]
        self.concurrent_downloads = self.raw["concurrent_downloads"]
        self.r34_api_key = self.raw["rule34"]["api_key"]
        self.r34_user_id = self.raw["rule34"]["user_id"]
        self.e621_api_key = self.raw["e621"]["api_key"]
        self.e621_user_id = self.raw["e621"]["user_id"]

    def load_fresh(self) -> None:
        raw = load_json(self.path, self.schema)
        if raw:
            self.raw = raw
        else:
            logging.info(f"Writing {self.path} with default values.")
            with open(self.path, "w") as f:
                json.dump(self.raw, f, indent=2)

        self.load()
        logging.info(f"Config loaded {self.censor()}")

    def save(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self.raw, f, indent=2)

        self.load()
        logging.info(f"Config saved {self.censor()}")

    def censor(self) -> dict:
        censored = self.raw.copy()
        for site in ["rule34", "e621"]:
            for key in ["api_key", "user_id"]:
                if censored[site][key]:
                    censored[site][key] = "CENSORED"
        return censored
