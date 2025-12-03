import platform
from pathlib import Path

import vdf


def get_steam_path() -> Path:
    # TODO: There can be other paths, maybe multiple?
    match platform.system():
        case "Linux":
            return Path("~/.local/share/Steam").expanduser()
        case "Windows":
            return Path("C:/Program Files (x86)/Steam")


def get_dir_names(parent: Path) -> list[str]:
    return [path.name for path in parent.iterdir() if path.is_dir()]


def get_game_ids() -> list[str]:
    return get_dir_names(get_steam_path() / "appcache" / "librarycache")


def get_user_ids() -> list[str]:
    return get_dir_names(get_steam_path() / "userdata")


def get_username_to_id() -> list[str]:
    steam_id3_list = get_user_ids()
    username_to_id = {}
    for steam_id3 in steam_id3_list:
        vdf_file = vdf.dumps(vdf.load(open(f"{get_steam_path()}/userdata/{steam_id3}/config/localconfig.vdf", encoding="utf8")))
        vdf_dict = vdf.loads(vdf_file)

        username_to_id[vdf_dict["UserLocalConfigStore"]["friends"]["PersonaName"]] = steam_id3
    return username_to_id


def get_grid_path(user_id: str) -> Path:
    return get_steam_path() / "userdata" / user_id / "config" / "grid"
