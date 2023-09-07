from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def io_dir(fixtures_dir: Path) -> Path:
    """Return the path to the io dir."""
    return Path(fixtures_dir, "io")


@pytest.fixture(scope="session")
def example_json_path(fixtures_dir: Path) -> Path:
    """Return a file path to example JSON file."""
    return Path(fixtures_dir, "io", "example_json.json")


@pytest.fixture(scope="session")
def example_yaml_path(io_dir: Path) -> Path:
    """Return the path to a example YAML file."""
    return Path(io_dir, "example_yaml.yaml")


@pytest.fixture(scope="session")
def csv_stream() -> str:
    """Return string with CSV format."""
    return """Lorem,ipsum,sit,amet
value_1,value_2,value_3,value_4"""
