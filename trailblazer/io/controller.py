from pathlib import Path
from typing import Any

from trailblazer.constants import FileFormat
from trailblazer.io.json import read_json
from trailblazer.io.yaml import read_yaml


class ReadFile:
    """Reading file using different methods."""

    read_file = {
        FileFormat.JSON: read_json,
        FileFormat.YAML: read_yaml,
    }

    @classmethod
    def get_content_from_file(cls, file_format: str, file_path: Path) -> Any:
        """Read file using file format dispatch table."""
        return cls.read_file[file_format](file_path=file_path)
