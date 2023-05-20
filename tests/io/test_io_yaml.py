from pathlib import Path

from trailblazer.io.yaml import read_yaml, write_yaml


def test_get_content_from_file(sample_data_path: Path):
    """
    Tests reading a YAML file
    """
    # GIVEN a YAML file

    # WHEN reading the YAML file
    sample_data_content: dict = read_yaml(file_path=sample_data_path)

    # Then assert a dict is returned
    assert isinstance(sample_data_content, dict)


def test_write_yaml(sample_data_path: Path, trailblazer_tmp_dir: Path):
    """
    Tests writing a file in YAML.
    """
    # GIVEN a YAML file

    # GIVEN a file path to write to
    yaml_file: Path = Path(trailblazer_tmp_dir, "write_yaml.yaml")

    # WHEN reading the YAML file
    sample_data_content: dict = read_yaml(file_path=sample_data_path)

    # WHEN writing the YAML file from dict
    write_yaml(content=sample_data_content, file_path=yaml_file)

    # THEN assert that a file was successfully created
    assert Path.exists(yaml_file)

    # WHEN reading it as a YAML
    written_sample_data_content: dict = read_yaml(file_path=yaml_file)

    # THEN assert that all data is kept
    assert sample_data_content == written_sample_data_content
