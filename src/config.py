import json
import logging
from pathlib import Path

from voluptuous import ALLOW_EXTRA, Any, Schema


class Config:
    def __init__(self) -> None:
        path = Path(__file__).parent.parent / "resources" / "config.json"

        schema = Schema(
            {
                "default_booru": Any("danbooru", "rule34"),
                "rule34": {
                    "api_key": Any(str, None),
                    "user_id": Any(int, None),
                },
            },
            required=True,
            extra=ALLOW_EXTRA,
        )

        # TODO: Write this as default
        config_dict = {
            "default_booru": "danbooru",
            "rule34": {
                "api_key": None,
                "user_id": None,
            },
        }

        if path.is_file():
            with open(path, "r") as f:
                config_dict = json.load(f)
            schema(config_dict)  # TODO: Error handling
            logging.info(f"Loading config {config_dict}")  # TODO: This logs API keys!

        self.default_booru = config_dict["default_booru"]
        self.r34_api_key = config_dict["rule34"]["api_key"]
        self.r34_user_id = config_dict["rule34"]["user_id"]
