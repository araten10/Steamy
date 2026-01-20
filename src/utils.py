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
from PIL import Image
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


def paste_logo(background: Path, logo: Path) -> Image:
    im1 = Image.open(background)
    im1x, im1y = im1.size
    im2 = Image.open(logo)

    # Resize logo because some things like the TF2 logo are insanely huge
    wpercent = (im1x * 0.90) / float(im2.size[0])
    im2_max_size = int((float(im2.size[1]) * float(wpercent)))
    im2 = im2.resize(((int(im1x * 0.90)), im2_max_size), Image.Resampling.LANCZOS)
    im2x, im2y = im2.size

    # Both images need to be the same size for alpha_composite to work, so we paste in both
    background = Image.new("RGBA", im1.size, (0, 0, 0))
    background.paste(im1)

    overlay_image = Image.new("RGBA", im1.size, (0, 0, 0))
    overlay_image.putalpha(0)
    overlay_pos_x = int((im1x * 0.50) - (im2x * 0.50))
    # TODO: add if toplogo im1y*0.10, if bottomlogo im1y*0.99-im2y, maybe random
    overlay_pos_y = int((im1y * 0.90) - im2y)
    overlay_image.paste(im2, (overlay_pos_x, overlay_pos_y))

    image = Image.alpha_composite(background, overlay_image)

    return image
