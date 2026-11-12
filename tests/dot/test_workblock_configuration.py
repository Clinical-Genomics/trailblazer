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
