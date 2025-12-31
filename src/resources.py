from pathlib import Path

ROOT = Path(__file__).parent.parent / "resources"

ICON = ROOT / "steamy.ico"
CONFIG = ROOT / "config.json"
GAME_DATABASE = ROOT / "game_database.json"

FONT_DIR = ROOT / "font"
FONTS = list(FONT_DIR.iterdir())

STYLE_DIR = ROOT / "qss"
STYLES = list(STYLE_DIR.iterdir())
