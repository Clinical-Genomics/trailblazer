from pathlib import Path
from typing import Any

import json
from trailblazer.constants import FileExtension
from trailblazer.io.validate_path import validate_file_suffix


def read_json(file_path: Path) -> Any:
    """Read content in a JSON file."""
    validate_file_suffix(path_to_validate=file_path, target_suffix=FileExtension.JSON)
    with open(file_path, "r") as file:
        return json.load(file)
