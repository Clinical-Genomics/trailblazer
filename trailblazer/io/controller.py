from pathlib import Path
from typing import Any

from trailblazer.constants import FileFormat
from trailblazer.io.yaml import read_yaml, write_yaml


class ReadFile:
    """Reading file using different methods."""

    read_file = {
        FileFormat.YAML: read_yaml,
    }

    @classmethod
    def get_content_from_file(cls, file_format: str, file_path: Path) -> Any:
        """Read file using file format dispatch table."""
        return cls.read_file[file_format](file_path=file_path)


class WriteFile:
    """Write file using different methods."""

    write_file = {
        FileFormat.YAML: write_yaml,
    }

    @classmethod
    def write_file_from_content(cls, content: Any, file_format: str, file_path: Path) -> None:
        """Write file using file format dispatch table."""
        cls.write_file[file_format](content=content, file_path=file_path)
