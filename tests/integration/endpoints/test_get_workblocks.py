from http import HTTPStatus

from flask.testing import FlaskClient

from trailblazer.store.database import get_session
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


def test_get_workblocks_without_edit_information(
    client: FlaskClient,
    workblock_configuration: WorkblockConfiguration,
):
    # GIVEN a saved workblock configuration without edit information
    workblock_configuration.updated_by = None
    workblock_configuration.updated_at = None
    session = get_session()
    session.commit()

    # WHEN retrieving the configuration
    response = client.get("/api/v1/workblocks")

    # THEN it returns the saved configuration with null edit information
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "version": workblock_configuration.version,
        "workblocks": workblock_configuration.workblocks,
        "updated_by": None,
        "updated_at": None,
    }


def test_get_workblocks_without_configuration(client: FlaskClient):
    # GIVEN no saved workblock configuration

    # WHEN retrieving the configuration
    response = client.get("/api/v1/workblocks")

    # THEN it returns a server error
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json == {"error": "An error occurred while processing your request."}
