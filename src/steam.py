import logging
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from time import sleep

import PyQt6.QtWidgets as QtW
import vdf

from utils import get_dir_names


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
        # TODO: There can be other paths, maybe multiple?
        match platform.system():
            case "Linux":
                self.path = Path("~/.local/share/Steam").expanduser()
            case "Windows":
                self.path = Path("C:/Program Files (x86)/Steam")
            case _:
                pass

        self.game_ids = get_dir_names(self.path / "appcache" / "librarycache")
        self.game_ids.sort(key=int)

        self.user_ids = get_dir_names(self.path / "userdata")

        self.usernames = []
        self.username_to_id = {}
        for user_id in self.user_ids:
            try:
                localconfig = self.path / "userdata" / user_id / "config" / "localconfig.vdf"
                vdf_str = vdf.dumps(vdf.load(open(localconfig, encoding="utf8")))
                vdf_dict = vdf.loads(vdf_str)

                username = vdf_dict["UserLocalConfigStore"]["friends"]["PersonaName"]
                self.usernames.append(username)
                self.username_to_id[username] = user_id
            except FileNotFoundError as e:
                logging.warning(f"Error opening USERID {user_id}: {e}. Skipping...")
                continue

    def restart(self) -> None:
        match platform.system():
            case "Linux":
                subprocess.run(["pkill", "steam"])

                # Wait until no Steam processes are found
                wait = True
                while wait:
                    sleep(0.5)
                    result = subprocess.run(["pgrep", "steam"], capture_output=True)
                    wait = result.returncode == 0

                subprocess.Popen(["steam"], start_new_session=True)
            case "Windows":
                subprocess.run(["taskkill", "/im", "steam.exe"])
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
