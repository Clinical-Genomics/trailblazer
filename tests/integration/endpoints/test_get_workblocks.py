from http import HTTPStatus

from flask.testing import FlaskClient

from trailblazer.store.models import WorkblockConfiguration


def test_get_workblocks(
    client: FlaskClient,
    workblock_configuration: WorkblockConfiguration,
):
    # GIVEN a saved workblock configuration

    # WHEN retrieving the configuration
    response = client.get("/api/v1/workblocks")

    # THEN it returns the saved configuration
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "version": workblock_configuration.version,
        "workblocks": workblock_configuration.workblocks,
        "updated_by": workblock_configuration.updated_by,
        "updated_at": workblock_configuration.updated_at.isoformat(),
    }
