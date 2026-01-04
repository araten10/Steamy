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

import logging
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from time import sleep

import PyQt6.QtWidgets as QtW
import vdf

from utils import get_dir_names, info_message


@dataclass
class Art:
    name: str  # Not required but useful for documentation
    suffix: str
    width: int
    height: int
    sample: bool

    # Lower is better
    def score(self, width: int, height: int) -> float:
        aspect_ratio_diff = abs(float(self.width) / self.height - float(width) / height)
        width_diff = abs(self.width - min(self.width, width))
        height_diff = abs(self.height - min(self.height, height))

        return width_diff + height_diff + aspect_ratio_diff


class Steam:
    def __init__(self) -> None:
        self.path = None
        match platform.system():
            case "Linux":
                self.linux_steam_args = ["steam"]
                for path, flatpak in [
                    (Path("~/.local/share/Steam").expanduser(), False),
                    (Path("~/.steam/root").expanduser(), False),
                    (Path("~/.var/app/com.valvesoftware.Steam/data/Steam").expanduser(), True),
                ]:
                    if path.is_dir():
                        self.path = path
                        if flatpak:
                            self.linux_steam_args = ["flatpak", "run", "com.valvesoftware.Steam"]
                        break
            case "Windows":
                for path in [
                    Path("C:/Program Files (x86)/Steam"),
                    Path("C:/Program Files/Steam"),
                ]:
                    if path.is_dir():
                        self.path = path
                        break

        if not self.path:
            info_message(QtW.QMessageBox.Icon.Critical, "Steam Not Found", "Could not find Steam installation location, unable to run.")
            sys.exit()

        self.game_ids = get_dir_names(self.path / "appcache" / "librarycache")
        self.game_ids.sort(key=int)

        self.user_ids = get_dir_names(self.path / "userdata")

        self.usernames = []
        self.username_to_id = {}
        for user_id in self.user_ids:
            localconfig = self.path / "userdata" / user_id / "config" / "localconfig.vdf"
            if not localconfig.is_file():
                logging.warning(f"User ID {user_id} has no localconfig.vdf file. Skipping...")
                continue

            vdf_str = vdf.dumps(vdf.load(open(localconfig, encoding="utf8")))
            vdf_dict = vdf.loads(vdf_str)

            username = vdf_dict["UserLocalConfigStore"]["friends"]["PersonaName"]
            self.usernames.append(username)
            self.username_to_id[username] = user_id

    def is_running(self) -> bool:
        # TODO: Are there other Steam processes we should check for?
        match platform.system():
            case "Linux":
                # Exact match only because otherwise this may catch unrelated processes
                res = subprocess.run(["pgrep", "-x", "steam"], capture_output=True)
                return res.returncode == 0
            case "Windows":
                res = subprocess.run(["tasklist", "/fi", "ImageName eq steam.exe", "/fo", "csv"], capture_output=True)
                return "steam.exe" in str(res.stdout)

    def restart(self) -> None:
        match platform.system():
            case "Linux":
                subprocess.run(["pkill", "-x", "steam"])

                while self.is_running():
                    sleep(0.5)

                subprocess.Popen(self.linux_steam_args, start_new_session=True)
            case "Windows":
                subprocess.run(["taskkill", "/f", "/im", "steam.exe"])

                while self.is_running():
                    sleep(0.5)

                subprocess.Popen([f"{self.path}/steam.exe"], creationflags=subprocess.DETACHED_PROCESS)


class Grid:
    def __init__(self, steam: Steam, username: str) -> None:
        config_path = steam.path / "userdata" / steam.username_to_id[username] / "config"

        self.path = config_path / "grid"
        self.porn_flag = self.path / "flag.steamy"

        self.custom_backup_path = config_path / "grid_custom_backup.steamy"
        self.porn_backup_path = config_path / "grid_porn_backup.steamy"

    def restore_backup(self, backup_path: Path) -> None:
        if not backup_path.exists():
            return

        if self.path.exists():
            logging.error(f"Cannot restore {type.lower()} art backup, grid path already exists")
            return

        shutil.move(backup_path, self.path)

    def make_backup(self) -> bool:
        if not self.path.exists():
            return True

        if self.porn_flag.is_file():
            backup_path = self.porn_backup_path
            type = "Porn"
        else:
            backup_path = self.custom_backup_path
            type = "Custom"

        if backup_path.exists():
            message = QtW.QMessageBox()
            message.setIcon(QtW.QMessageBox.Icon.Question)
            message.setText(f"{type} Art Backup Exists")
            message.setInformativeText(
                f"A {type.lower()} art backup already exists. Do you want to "
                "overwrite your backup or keep your current backup and delete "
                f"your current {type.lower()} art?"
            )

            overwrite = message.addButton("Overwrite backup", QtW.QMessageBox.ButtonRole.DestructiveRole)
            delete = message.addButton("Delete current art", QtW.QMessageBox.ButtonRole.DestructiveRole)
            message.addButton(QtW.QMessageBox.StandardButton.Cancel)
            message.exec()

            if message.clickedButton() == overwrite:
                shutil.rmtree(backup_path)
                shutil.move(self.path, backup_path)
            elif message.clickedButton() == delete:
                shutil.rmtree(self.path)
            else:
                return False
        else:
            shutil.move(self.path, backup_path)

        return True
