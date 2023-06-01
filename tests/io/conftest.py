from pathlib import Path

import pytest


@pytest.fixture(scope="session", name="io_dir")
def fixture_io_dir(fixtures_dir: Path) -> Path:
    """Return the path to the io dir."""
    return Path(fixtures_dir, "io")


@pytest.fixture(scope="session", name="example_yaml_path")
def fixture_example_yaml_path(io_dir: Path) -> Path:
    """Return the path to a example YAML file."""
    return Path(io_dir, "example_yaml.yaml")
