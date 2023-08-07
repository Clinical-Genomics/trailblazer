from pathlib import Path

from trailblazer.constants import FileFormat
from trailblazer.io.controller import ReadFile, ReadStream


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


def test_get_content_from_file_when_json(example_json_path: Path):
    """
    Tests get content from file when JSON.
    """
    # GIVEN a JSON file

    # WHEN reading the JSON file
    json_content: dict = ReadFile.get_content_from_file(
        file_format=FileFormat.JSON, file_path=example_json_path
    )

    # Then assert a dict is returned
    assert isinstance(json_content, dict)


def test_get_content_from_stream_when_csv(csv_stream: str):
    """Tests read a CSV stream."""
    # GIVEN a string in CSV format

    # WHEN reading the CSV content in string
    raw_csv_content: list = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV, stream=csv_stream
    )

    # THEN assert that a list is returned
    assert isinstance(raw_csv_content, list)


def test_get_content_from_stream_when_csv_when_dict(csv_stream: str):
    """Tests read a CSV stream into a dict."""
    # GIVEN a string in CSV format

    # WHEN reading the CSV content in string
    raw_csv_content: list = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=csv_stream,
        read_to_dict=True,
    )

    # Then assert a list is returned and that the first element is a dict
    assert isinstance(raw_csv_content, list)
    assert isinstance(raw_csv_content[0], dict)
