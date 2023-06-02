from pathlib import Path

from trailblazer.io.json import read_json


def test_get_content_from_file(example_json_path: Path):
    """
    Tests read JSON content from file.
    """
    # GIVEN a JSON file

    # WHEN reading the JSON file
    raw_json_content: dict = read_json(file_path=example_json_path)

    # Then assert a dict is returned
    assert isinstance(raw_json_content, dict)

    # THEN assert the content is unchanged
    assert raw_json_content == {"glossary": {"title": "example glossary"}}
