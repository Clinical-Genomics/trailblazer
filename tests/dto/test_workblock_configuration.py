import pytest
from pydantic import ValidationError

from trailblazer.dto.workblock_configuration import WorkblockConfigurationRequest


def test_valid_workblock_configuration():
    # GIVEN a valid configuration
    data = {
        "version": 1,
        "workblocks": [
            {
                "id": "workblock-1",
                "name": "Workblock 1",
                "color": "#8dd909",
                "workflows": ["nallo"],
            }
        ],
    }

    # WHEN validating the configuration
    configuration = WorkblockConfigurationRequest.model_validate(data)

    # THEN it accepts the configuration
    assert configuration.model_dump() == data


def test_workblock_configuration_with_duplicate_ids():
    # GIVEN an invalid configuration with duplicate workblock IDs
    data = {
        "version": 1,
        "workblocks": [
            {
                "id": "workblock-1",
                "name": "Workblock 1",
                "color": "#8dd909",
                "workflows": ["nallo"],
            },
            {
                "id": "workblock-1",
                "name": "Workblock 2",
                "color": "#ff5733",
                "workflows": ["balsamic"],
            },
        ],
    }

    # WHEN validating, THEN duplicate workblock IDs are rejected
    with pytest.raises(ValidationError, match="Duplicate workblock ID: workblock-1"):
        WorkblockConfigurationRequest.model_validate(data)
