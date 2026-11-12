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


def test_workblock_configuration_with_duplicate_workflows():
    # GIVEN two blocks containing the same workflow
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
                "id": "workblock-2",
                "name": "Workblock 2",
                "color": "#d57012",
                "workflows": ["nallo"],
            },
        ],
    }

    # WHEN validating, THEN duplicate workflows are rejected
    with pytest.raises(
        ValidationError,
        match="Workflow assigned more than once: nallo",
    ):
        WorkblockConfigurationRequest.model_validate(data)


def test_workblock_configuration_without_workblocks():
    # GIVEN a configuration without workblocks
    data = {"version": 1, "workblocks": []}

    # WHEN validating, THEN an empty list is rejected
    with pytest.raises(ValidationError) as error:
        WorkblockConfigurationRequest.model_validate(data)

    assert error.value.errors()[0]["loc"] == ("workblocks",)
    assert error.value.errors()[0]["type"] == "too_short"


def test_workblock_configuration_with_too_many_workblocks():
    # GIVEN six blocks with unique IDs and workflows
    workflows = ["nallo", "tomte", "fluffy", "balsamic", "rnafusion", "microsalt"]
    data = {
        "version": 1,
        "workblocks": [
            {
                "id": f"workblock-{index}",
                "name": f"Workblock {index}",
                "color": "#8dd909",
                "workflows": [workflow],
            }
            for index, workflow in enumerate(workflows, start=1)
        ],
    }

    # WHEN validating, THEN more than five blocks are rejected
    with pytest.raises(ValidationError) as error:
        WorkblockConfigurationRequest.model_validate(data)

    assert error.value.errors()[0]["loc"] == ("workblocks",)
    assert error.value.errors()[0]["type"] == "too_long"


@pytest.mark.parametrize(
    "field, value",
    [
        ("name", ""),
        ("name", "   "),
        ("name", "a" * 129),
        ("color", "red"),
        ("color", "#12345"),
        ("color", "#gggggg"),
    ],
)
def test_workblock_configuration_with_invalid_name_or_color(field, value):
    # GIVEN a block with an invalid name or color
    workblock = {
        "id": "workblock-1",
        "name": "Workblock 1",
        "color": "#8dd909",
        "workflows": ["nallo"],
    }
    workblock[field] = value

    data = {"version": 1, "workblocks": [workblock]}

    # WHEN validating, THEN the invalid field is rejected
    with pytest.raises(ValidationError) as error:
        WorkblockConfigurationRequest.model_validate(data)

    assert error.value.errors()[0]["loc"] == ("workblocks", 0, field)


def test_workblock_configuration_with_unknown_workflow():
    # GIVEN a block with unknown workflow
    data = {
        "version": 1,
        "workblocks": [
            {
                "id": "workblock-1",
                "name": "Workblock 1",
                "color": "#8dd909",
                "workflows": ["unknown"],
            }
        ],
    }

    # WHEN validating, THEN the unknown workflow is rejected
    with pytest.raises(ValidationError, match="Unsupported workflow: unknown"):
        WorkblockConfigurationRequest.model_validate(data)


def test_workblock_configuration_with_empty_workflow_list():
    # GIVEN a block with an empty workflow list
    data = {
        "version": 1,
        "workblocks": [
            {
                "id": "workblock-1",
                "name": "Workblock 1",
                "color": "#8dd909",
                "workflows": [],
            }
        ],
    }

    # WHEN validating, THEN the empty workflow list is rejected
    with pytest.raises(ValidationError, match="List should have at least 1 item"):
        WorkblockConfigurationRequest.model_validate(data)
