import platform
from dataclasses import dataclass
from pathlib import Path

import vdf


def get_dir_names(parent: Path) -> list[str]:
    return [path.name for path in parent.iterdir() if path.is_dir()]


@dataclass
class Art:
    name: str  # Not required but useful for documentation
    suffix: str
    width: int
    height: int

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
        self.user_ids = get_dir_names(self.path / "userdata")

        self.usernames = []
        self.username_to_id = {}
        for user_id in self.user_ids:
            localconfig = self.path / "userdata" / user_id / "config" / "localconfig.vdf"
            vdf_str = vdf.dumps(vdf.load(open(localconfig, encoding="utf8")))
            vdf_dict = vdf.loads(vdf_str)

            username = vdf_dict["UserLocalConfigStore"]["friends"]["PersonaName"]
            self.usernames.append(username)
            self.username_to_id[username] = user_id

    def get_grid_path(self, username: str) -> Path:
        return self.path / "userdata" / self.username_to_id[username] / "config" / "grid"
