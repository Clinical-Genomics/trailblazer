"""Module to read or write YAML files."""
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


def write_yaml(content: Any, file_path: Path) -> None:
    """Write content to a YAML file."""
    yaml: YAML = YAML()
    yaml.default_flow_style = False
    yaml.dump(content, file_path)
