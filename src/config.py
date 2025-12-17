import json
import logging
from pathlib import Path

from voluptuous import ALLOW_EXTRA, Any, Schema


class Config:
    def __init__(self) -> None:
        self.path = Path(__file__).parent.parent / "resources" / "config.json"

        self.supported_boorus = ["danbooru", "rule34"]
        self.schema = Schema(
            {
                "default_booru": Any(*self.supported_boorus),
                "rule34": {
                    "api_key": Any(str, None),
                    "user_id": Any(int, None),
                },
            },
            required=True,
            extra=ALLOW_EXTRA,
        )

        # TODO: Write this as default
        self.raw = {
            "default_booru": "danbooru",
            "rule34": {
                "api_key": None,
                "user_id": None,
            },
        }

        self.load_fresh()

    def load(self) -> None:
        self.default_booru = self.raw["default_booru"]
        self.r34_api_key = self.raw["rule34"]["api_key"]
        self.r34_user_id = self.raw["rule34"]["user_id"]

    def load_fresh(self) -> None:
        if self.path.is_file():
            with open(self.path, "r") as f:
                self.raw = json.load(f)
            self.schema(self.raw)  # TODO: Error handling

        self.load()
        logging.info(f"Config loaded {self.raw}")  # TODO: This logs API keys!

    def save(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self.raw, f, indent=2)

        self.load()
        logging.info(f"Config saved {self.raw}")  # TODO: This logs API keys!
