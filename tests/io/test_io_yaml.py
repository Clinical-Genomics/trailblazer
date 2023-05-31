from pathlib import Path

from trailblazer.io.yaml import read_yaml


def test_get_content_from_file(sample_data_path: Path):
    """
    Tests reading a YAML file.
    """
    # GIVEN a YAML file

    # WHEN reading the YAML file
    sample_data_content: dict = read_yaml(file_path=sample_data_path)

    # Then assert a dict is returned
    assert isinstance(sample_data_content, dict)

    # Then assert we can access returned dict
    assert sample_data_content.get("users")
