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
