import json
import logging
from json.decoder import JSONDecodeError
from pathlib import Path

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


def get_dir_names(parent: Path) -> list[str]:
    return [path.name for path in parent.iterdir() if path.is_dir()]


def get_nested(d: dict, keys: list[str]) -> object:
    value = d
    for key in keys:
        value = value[key]
    return value
