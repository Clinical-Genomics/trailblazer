"""Module to read YAML files."""
from pathlib import Path
from typing import Any
from ruamel.yaml import YAML

from trailblazer.constants import FileExtension
from trailblazer.io.validate_path import validate_file_suffix


def read_yaml(file_path: Path) -> Any:
    """Read content in a YAML file."""
    validate_file_suffix(path_to_validate=file_path, target_suffix=FileExtension.YAML)
    yaml: YAML = YAML(typ="safe", pure=True)
    return yaml.load(file_path)
