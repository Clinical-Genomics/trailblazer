import pytest

from trailblazer.dto.workblock_configuration import WorkblockConfigurationRequest
from trailblazer.exc import WorkblockConfigurationConflictError


def test_update_workblock_configuration(workblock_service, user, workblock_configuration):
    # GIVEN a workblock configuration and a user
    workblock_config = WorkblockConfigurationRequest.model_validate(
        {
            "version": 1,
            "workblocks": [
                {
                    "id": "wb1",
                    "name": "Workblock 1",
                    "color": "#FF5733",
                    "workflows": ["nallo"],
                },
                {
                    "id": "wb2",
                    "name": "Workblock 2",
                    "color": "#33FF57",
                    "workflows": ["balsamic"],
                },
            ],
        }
    )

    # WHEN saving the new configuration
    response = workblock_service.update_workblock_configuration(data=workblock_config, user=user)

    # THEN it returns the updated configuration
    assert response.version == workblock_config.version + 1
    assert response.workblocks == workblock_config.workblocks
    assert response.updated_by == user.abbreviation
    assert response.updated_at is not None

    # THEN the changes are saved in the database
    saved_config = workblock_service.get_workblock_configuration()
    assert saved_config.version == response.version
    assert saved_config.workblocks == response.workblocks
    assert saved_config.updated_by == user.abbreviation
    assert saved_config.updated_at == response.updated_at


def test_update_workblock_configuration_with_outdated_version(
    workblock_service, user, workblock_configuration
):
    # GIVEN a workblock configuration and a user
    workblock_config = WorkblockConfigurationRequest.model_validate(
        {
            "version": 1,
            "workblocks": [
                {
                    "id": "wb1",
                    "name": "Workblock 1",
                    "color": "#FF5733",
                    "workflows": ["nallo"],
                },
                {
                    "id": "wb2",
                    "name": "Workblock 2",
                    "color": "#33FF57",
                    "workflows": ["balsamic"],
                },
            ],
        }
    )

    # GIVEN a successful save that advances the database version
    saved = workblock_service.update_workblock_configuration(data=workblock_config, user=user)
    assert saved.version == 2

    # WHEN saving the old version, THEN it is rejected
    with pytest.raises(WorkblockConfigurationConflictError):
        workblock_service.update_workblock_configuration(data=workblock_config, user=user)

    # THEN the saved configuration and edit information remain unchanged
    assert workblock_service.get_workblock_configuration() == saved


def test_update_workblock_configuration_without_changes():
    pass


def test_update_workblock_configuration_rolls_back_on_failure():
    pass


def test_update_workblock_configuration_with_concurrent_edits():
    pass
