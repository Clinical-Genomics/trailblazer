from pathlib import Path

from trailblazer.constants import FileFormat
from trailblazer.io.controller import ReadFile


def test_get_content_from_file(sample_data_path: Path):
    """
    Tests get content from file.
    """
    # GIVEN a YAML file

    # WHEN reading the YAML file
    sample_data_content: dict = ReadFile.get_content_from_file(
        file_format=FileFormat.YAML, file_path=sample_data_path
    )

    # Then assert a dict is returned
    assert isinstance(sample_data_content, dict)
