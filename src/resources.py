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

from pathlib import Path

ROOT = Path(__file__).parent.parent / "resources"

ICON = ROOT / "steamy.ico"
CONFIG = ROOT / "config.json"
GAME_DATABASE = ROOT / "game_database.json"

FONT_DIR = ROOT / "font"
FONTS = list(FONT_DIR.iterdir())

STYLE_DIR = ROOT / "qss"
STYLES = list(STYLE_DIR.iterdir())
