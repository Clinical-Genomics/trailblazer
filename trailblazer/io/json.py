from pathlib import Path
from typing import Any

import json


def read_json(file_path: Path) -> Any:
    """Read content in a JSON file."""
    with open(file_path, "r") as file:
        return json.load(file)
