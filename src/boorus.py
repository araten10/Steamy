import json
from pathlib import Path

import booru

from games import Game

# TODO: This is bad, refactor!!!
config_path = Path(__file__).parent.parent / "resources" / "config.json"
config = None
if config_path.exists():
    with open(config_path, "r") as f:
        config = json.load(f)


class SteamyDanbooru(booru.Danbooru):
    def __init__(self) -> None:
        super().__init__()

        self.base_query = "order:random"
        self.fallback_query = "age:<1month"

        self.file_url = "file_url"
        self.sample_url = "large_file_url"
        self.width = "image_width"
        self.height = "image_height"
        self.rate_limit = 0.1

    async def search(self, game: Game) -> str:
        query = f"{game.danbooru or self.fallback_query} {self.base_query}"
        return await super().search(query=query)

    def filter_images(self, posts: list) -> list:
        return list(filter(lambda post: post["file_ext"] in ["png", "jpg", "jpeg"], posts))


class SteamyRule34(booru.Rule34):
    def __init__(self) -> None:
        super().__init__()
        self.specs = {"api_key": config["rule34"]["api_key"], "user_id": config["rule34"]["user_id"]}

        self.base_query = "sort:random score:>500 -video -animated"
        self.fallback_query = "-rating:safe"

        self.file_url = "file_url"
        self.sample_url = "sample_url"
        self.width = "width"
        self.height = "height"
        self.rate_limit = 1

    async def search(self, game: Game) -> str:
        query = f"{game.rule34 or self.fallback_query} {self.base_query}"
        return await super().search(query=query)

    def filter_images(self, posts: list) -> list:
        return list(filter(lambda post: post["file_url"].split(".")[-1] in ["png", "jpg", "jpeg"], posts))


def get_booru() -> SteamyDanbooru | SteamyRule34:
    boorus = {
        "danbooru": SteamyDanbooru(),
        "rule34": SteamyRule34(),
    }
    return boorus[config["default_booru"]]
