# -*- coding: utf-8 -*-
import pytest

from tests.conftest import MockTowerAPI, TowerResponseFile
from trailblazer.constants import TrailblazerStatus


@pytest.mark.parametrize(
    "response_file, expected_status",
    [
        (TowerResponseFile.PENDING, TrailblazerStatus.PENDING.value),
        (TowerResponseFile.RUNNING, TrailblazerStatus.RUNNING.value),
        (TowerResponseFile.COMPLETED, TrailblazerStatus.COMPLETED.value),
    ],
)
def test_TowerAPI_status(tower_config_file: str, response_file: str, expected_status: str) -> None:
    """Assess that TowerAPI returns the correct status given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(id_file=tower_config_file)
    tower_api.mock_query(response_file=response_file)

    # THEN status should be as expected according to the mocked response
    assert tower_api.status == expected_status


@pytest.mark.parametrize(
    "response_file, expected_bool",
    [
        (TowerResponseFile.PENDING, True),
        (TowerResponseFile.RUNNING, False),
        (TowerResponseFile.COMPLETED, False),
    ],
)
def test_TowerAPI_is_pending(
    tower_config_file: str, response_file: str, expected_bool: bool
) -> None:
    """Assess that TowerAPI returns the state for is_pending given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(id_file=tower_config_file)
    tower_api.mock_query(response_file=response_file)

    # THEN is_pending should be as expected according to the mocked response
    assert tower_api.is_pending == expected_bool


@pytest.mark.parametrize(
    "response_file, expected_total_jobs",
    [
        (TowerResponseFile.PENDING, 0),
        (TowerResponseFile.RUNNING, 13),
        (TowerResponseFile.COMPLETED, 13),
    ],
)
def test_TowerAPI_total_jobs(
    tower_config_file: str, response_file: str, expected_total_jobs: int
) -> None:
    """Assess that TowerAPI correctly returns the total number jobs given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(id_file=tower_config_file)
    tower_api.mock_query(response_file=response_file)

    # THEN total_jobs should be as expected according to the mocked response
    assert tower_api.total_jobs == expected_total_jobs


@pytest.mark.parametrize(
    "response_file, expected_succeeded_jobs",
    [
        (TowerResponseFile.PENDING, 0),
        (TowerResponseFile.RUNNING, 2),
        (TowerResponseFile.COMPLETED, 6),
    ],
)
def test_TowerAPI_succeeded_jobs(
    tower_config_file: str, response_file: str, expected_succeeded_jobs: int
) -> None:
    """Assess that TowerAPI correctly returns the number of succeeded jobs given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(id_file=tower_config_file)
    tower_api.mock_query(response_file=response_file)

    # THEN total_jobs should be as expected according to the mocked response
    assert tower_api.succeeded_jobs == expected_succeeded_jobs


@pytest.mark.parametrize(
    "response_file, expected_succeeded_jobs",
    [
        (TowerResponseFile.PENDING, 0),
        (TowerResponseFile.RUNNING, 2),
        (TowerResponseFile.COMPLETED, 6),
    ],
)
def test_TowerAPI_succeeded_jobs(
    tower_config_file: str, response_file: str, expected_succeeded_jobs: int
) -> None:
    """Assess that TowerAPI correctly returns the number of succeeded jobs given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(id_file=tower_config_file)
    tower_api.mock_query(response_file=response_file)

    # THEN total_jobs should be as expected according to the mocked response
    assert tower_api.succeeded_jobs == expected_succeeded_jobs


@pytest.mark.parametrize(
    "response_file, expected_progress",
    [
        (TowerResponseFile.PENDING, 0),
        (TowerResponseFile.RUNNING, 15),
        (TowerResponseFile.COMPLETED, 100),
    ],
)
def test_TowerAPI_progress(
    tower_config_file: str, response_file: str, expected_progress: int
) -> None:
    """Assess that TowerAPI returns the progress percentage given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(id_file=tower_config_file)
    tower_api.mock_query(response_file=response_file)

    # THEN total_jobs should be as expected according to the mocked response
    assert tower_api.progress == expected_progress
