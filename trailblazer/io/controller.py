from pathlib import Path
from typing import Any, Callable

from trailblazer.constants import FileFormat
from trailblazer.io.csv import read_csv_stream
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


class ReadStream:
    """Reading stream using different methods."""

    read_stream: dict[str, Callable] = {
        FileFormat.CSV: read_csv_stream,
    }

    @classmethod
    def get_content_from_stream(cls, file_format: str, stream: Any, **kwargs) -> Any:
        """Read stream using file format dispatch table."""
        return cls.read_stream[file_format](stream=stream, **kwargs)
