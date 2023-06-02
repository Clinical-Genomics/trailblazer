from pathlib import Path

import pytest


@pytest.fixture(name="io_dir", scope="session")
def fixture_io_dir(fixtures_dir: Path) -> Path:
    """Return the path to the io dir."""
    return Path(fixtures_dir, "io")


@pytest.fixture(name="example_json_path", scope="session")
def fixture_example_json_path(fixtures_dir: Path) -> Path:
    """Return a file path to example JSON file."""
    return Path(fixtures_dir, "io", "example_json.json")


@pytest.fixture(name="example_yaml_path", scope="session")
def fixture_example_yaml_path(io_dir: Path) -> Path:
    """Return the path to a example YAML file."""
    return Path(io_dir, "example_yaml.yaml")
