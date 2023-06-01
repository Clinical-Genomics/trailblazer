from pathlib import Path

from trailblazer.io.yaml import read_yaml


def test_get_content_from_file(example_yaml_path: Path):
    """
    Tests reading a YAML file.
    """
    # GIVEN a YAML file

    # WHEN reading the YAML file
    yaml_content: dict = read_yaml(file_path=example_yaml_path)

    # Then assert a dict is returned
    assert isinstance(yaml_content, dict)

    # Then assert content is unchanged
    assert yaml_content == {
        "users": [
            {"name": "Paul Anderson"},
        ],
    }
