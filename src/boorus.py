import booru
import PyQt6.QtWidgets as QtW

from config import Config
from games import Game


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

    def filter(self, posts: list) -> list:
        # Filter out non-images and removed posts
        return list(filter(lambda post: post["file_ext"] in ["png", "jpg", "jpeg"] and "file_url" in post, posts))


class SteamyRule34(booru.Rule34):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.specs = {"api_key": config.r34_api_key, "user_id": config.r34_user_id}

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

    def filter(self, posts: list) -> list:
        return list(filter(lambda post: post["file_url"].split(".")[-1] in ["png", "jpg", "jpeg"], posts))


class SteamyE621(booru.E621):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.specs = {"api_key": config.e621_api_key, "login": config.e621_user_id}

        self.base_query = "order:random score:>500 -animated"
        self.fallback_query = "-rating:safe"

        self.file_url = "file_url"
        self.sample_url = "sample_url"
        self.width = "width"
        self.height = "height"
        self.rate_limit = 1

    async def search(self, game: Game) -> str:
        query = f"{game.e621 or self.fallback_query} {self.base_query}"
        return await super().search(query=query)

    def filter(self, posts: list) -> list:
        return list(filter(lambda post: post["file_url"].split(".")[-1] in ["png", "jpg", "jpeg"], posts))


async def get_booru(config: Config) -> SteamyDanbooru | SteamyRule34 | SteamyE621 | None:
    option = None
    match config.default_booru:
        case "rule34" if config.r34_api_key and config.r34_user_id:
            option = SteamyRule34(config)
        case "e621" if config.e621_api_key and config.e621_user_id:
            option = SteamyE621(config)

    test_error = False
    if option:
        try:
            await option.search(Game(""))
        except Exception:
            test_error = True

    if (config.default_booru != "danbooru" and not option) or test_error:
        message = QtW.QMessageBox()
        message.setIcon(QtW.QMessageBox.Icon.Warning)
        message.setText(f"Can't Use {config.default_booru}")
        message.setInformativeText("Make sure you have provided your API key and user ID and that they are correct.")
        message.setStandardButtons(QtW.QMessageBox.StandardButton.Ok)
        message.exec()
        return

    return option or SteamyDanbooru()
