"""Module to read or write YAML files."""
from pathlib import Path
from typing import Any
from ruamel.yaml import YAML


def read_yaml(file_path: Path) -> Any:
    """Read content in a YAML file."""
    yaml: YAML = YAML(typ="safe")
    return yaml.load(file_path)


def write_yaml(content: Any, file_path: Path) -> None:
    """Write content to a YAML file."""
    yaml: YAML = YAML()
    yaml.default_flow_style = False
    yaml.dump(content, file_path)
