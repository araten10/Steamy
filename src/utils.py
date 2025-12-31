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

import json
import logging
from json.decoder import JSONDecodeError
from pathlib import Path

import PyQt6.QtWidgets as QtW
from voluptuous import Schema
from voluptuous.error import Invalid


def load_json(path: Path, schema: Schema) -> dict | None:
    try:
        with open(path) as f:
            data = json.load(f)
            schema(data)
            logging.info(f"{path} loaded successfully.")
            return data
    except FileNotFoundError:
        logging.info(f"{path} not found.")
    except JSONDecodeError as e:
        logging.warning(f"{path} is not valid JSON. Reason: {e}")
    except Invalid as e:
        logging.warning(f"{path} format is invalid. Reason: {e}")

    return None


def info_message(icon: QtW.QMessageBox.Icon, text: str, informative_text: str) -> None:
    message = QtW.QMessageBox()
    message.setIcon(icon)
    message.setText(text)
    message.setInformativeText(informative_text)
    message.setStandardButtons(QtW.QMessageBox.StandardButton.Ok)
    message.exec()


def get_dir_names(parent: Path) -> list[str]:
    return [path.name for path in parent.iterdir() if path.is_dir()]


def get_nested(d: dict, keys: list[str]) -> object:
    value = d
    for key in keys:
        value = value[key]
    return value
