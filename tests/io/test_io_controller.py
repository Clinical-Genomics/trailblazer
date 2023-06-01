from pathlib import Path

from trailblazer.constants import FileFormat
from trailblazer.io.controller import ReadFile


def test_get_content_from_file(example_yaml_path: Path):
    """
    Tests get content from file.
    """
    # GIVEN a YAML file

    # WHEN reading the YAML file
    yaml_content: dict = ReadFile.get_content_from_file(
        file_format=FileFormat.YAML, file_path=example_yaml_path
    )

    # Then assert a dict is returned
    assert isinstance(yaml_content, dict)
