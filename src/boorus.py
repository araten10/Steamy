# Copyright (C) 2026 Araten & Marigold
#
# This file is part of Steamy.
#
# Steamy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Steamy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Steamy.  If not, see <https://www.gnu.org/licenses/>.

import booru
import PyQt6.QtWidgets as QtW

from config import Config
from games import Game
from utils import info_message


class SteamyDanbooru(booru.Danbooru):
    def __init__(self, config: Config) -> None:
        super().__init__()

        self.base_query = config.dan_base_query
        self.fallback_query = config.dan_fallback_query

        self.file_url = ["file_url"]
        self.sample_url = ["large_file_url"]
        self.width = ["image_width"]
        self.height = ["image_height"]
        self.rate_limit = 0.1

    def get_query(self, game: Game) -> str:
        return f"{game.danbooru or self.fallback_query} {self.base_query}"

    async def search(self, game: Game) -> str:
        return await super().search(query=self.get_query(game))

    def filter(self, posts: list) -> list:
        # Filter out non-images and removed posts
        return list(filter(lambda post: post["file_ext"] in ["png", "jpg", "jpeg"] and "file_url" in post, posts))


class SteamyRule34(booru.Rule34):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.specs = {"api_key": config.r34_api_key, "user_id": config.r34_user_id}

        self.base_query = config.r34_base_query
        self.fallback_query = config.r34_fallback_query

        self.file_url = ["file_url"]
        self.sample_url = ["sample_url"]
        self.width = ["width"]
        self.height = ["height"]
        self.rate_limit = 1

    def get_query(self, game: Game) -> str:
        return f"{game.rule34 or self.fallback_query} {self.base_query}"

    async def search(self, game: Game) -> str:
        return await super().search(query=self.get_query(game))

    def filter(self, posts: list) -> list:
        return list(filter(lambda post: post["file_url"].split(".")[-1] in ["png", "jpg", "jpeg"], posts))


class SteamyE621(booru.E621):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.specs = {"api_key": config.e621_api_key, "login": config.e621_username}

        self.base_query = config.e621_base_query
        self.fallback_query = config.e621_fallback_query

        self.file_url = ["file", "url"]
        self.sample_url = ["sample", "url"]
        self.width = ["file", "width"]
        self.height = ["file", "height"]
        self.rate_limit = 1

    def get_query(self, game: Game) -> str:
        return f"{game.e621 or self.fallback_query} {self.base_query}"

    async def search(self, game: Game) -> str:
        return await super().search(query=self.get_query(game))

    def filter(self, posts: list) -> list:
        return list(filter(lambda post: post["file"]["ext"] in ["png", "jpg", "jpeg"], posts))


async def get_booru(config: Config) -> SteamyDanbooru | SteamyRule34 | SteamyE621 | None:
    option = None
    match config.default_booru:
        case "rule34" if config.r34_api_key and config.r34_user_id:
            option = SteamyRule34(config)
        case "e621" if config.e621_api_key and config.e621_username:
            option = SteamyE621(config)

    test_error = False
    if option:
        try:
            await option.search(Game(""))
        except Exception:
            test_error = True

    if (config.default_booru != "danbooru" and not option) or test_error:
        info_message(
            QtW.QMessageBox.Icon.Warning,
            f"Can't Use {config.default_booru}",
            "Make sure you have provided your API key and user ID or username and that they are correct.",
        )
        return

    return option or SteamyDanbooru(config)
