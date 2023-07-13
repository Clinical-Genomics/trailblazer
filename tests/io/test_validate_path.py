from pathlib import Path

import pytest

from trailblazer.constants import FileExtension
from trailblazer.exc import ValidationError
from trailblazer.io.validate_path import validate_file_suffix


def test_validate_file_suffix_correct_suffix(analysis_data_path: Path):
    """Test validate file suffix when file suffix is in correct format."""
    # GIVEN a path in the correct file format

    # WHEN validating the file suffix
    was_validated: bool = validate_file_suffix(
        path_to_validate=analysis_data_path, target_suffix=FileExtension.YAML
    )

    # THEN assert the suffix is in the correct format
    assert was_validated


def test_validate_file_suffix_wrong_suffix(caplog):
    """Test validate file suffix when file suffix is in wrong format."""
    # GIVEN path in the wrong file format
    file_path: Path = Path("file.json")
    assert file_path.suffix != FileExtension.YAML

    # WHEN validating the file suffix
    with pytest.raises(ValidationError):
        validate_file_suffix(path_to_validate=file_path, target_suffix=FileExtension.YAML)

        # THEN assert the suffix is in the wrong format
        assert "seems to be in wrong format" in caplog.text
