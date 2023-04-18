from pathlib import Path
from typing import List

import pytest

from tests.apps.tower.conftest import TowerResponseFile
from tests.mocks.tower_mock import MockTowerAPI
from trailblazer.apps.tower.models import TowerTask
from trailblazer.constants import TrailblazerStatus


@pytest.mark.parametrize(
    "response_file, expected_status",
    [
        (TowerResponseFile.PENDING, TrailblazerStatus.PENDING.value),
        (TowerResponseFile.RUNNING, TrailblazerStatus.RUNNING.value),
        (TowerResponseFile.COMPLETED, TrailblazerStatus.COMPLETED.value),
    ],
)
def test_tower_api_status(tower_id: str, response_file: Path, expected_status: str) -> None:
    """Assess that TowerAPI returns the correct status given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(workflow_id=tower_id)
    tower_api.mock_query(response_file=response_file)

    # THEN a trailblazer status is returned
    assert tower_api.status == expected_status


@pytest.mark.parametrize(
    "response_file, expected_bool",
    [
        (TowerResponseFile.PENDING, True),
        (TowerResponseFile.RUNNING, False),
        (TowerResponseFile.COMPLETED, False),
    ],
)
def test_tower_api_is_pending(tower_id: str, response_file: Path, expected_bool: bool) -> None:
    """Assess that TowerAPI returns the state for is_pending given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(workflow_id=tower_id)
    tower_api.mock_query(response_file=response_file)

    # THEN is_pending should be returned
    assert tower_api.is_pending == expected_bool


@pytest.mark.parametrize(
    "response_file, expected_nr_total_jobs",
    [
        # (TowerResponseFile.PENDING, 0),
        (TowerResponseFile.RUNNING, 13),
        (TowerResponseFile.COMPLETED, 13),
    ],
)
def test_tower_api_total_jobs(
    tower_id: str, response_file: Path, expected_nr_total_jobs: int
) -> None:
    """Assess that TowerAPI correctly returns the total number of potential jobs given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(workflow_id=tower_id)
    tower_api.mock_query(response_file=response_file)

    # THEN the total number of potential jobs is returned
    assert tower_api.total_jobs == expected_nr_total_jobs


@pytest.mark.parametrize(
    "response_file, expected_succeeded_jobs",
    [
        (TowerResponseFile.PENDING, 0),
        (TowerResponseFile.RUNNING, 2),
        (TowerResponseFile.COMPLETED, 6),
    ],
)
def test_tower_api_succeeded_jobs(
    tower_id: str, response_file: Path, expected_succeeded_jobs: int
) -> None:
    """Assess that TowerAPI correctly returns the number of succeeded jobs given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(workflow_id=tower_id)
    tower_api.mock_query(response_file=response_file)

    # THEN the total number of succeeded jobs is returned
    assert tower_api.succeeded_jobs == expected_succeeded_jobs


@pytest.mark.parametrize(
    "response_file, expected_progress",
    [
        (TowerResponseFile.PENDING, 0),
        (TowerResponseFile.RUNNING, 15),
        (TowerResponseFile.COMPLETED, 100),
    ],
)
def test_tower_api_progress(tower_id: str, response_file: Path, expected_progress: int) -> None:
    """Assess that TowerAPI returns the progress percentage given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(workflow_id=tower_id)
    tower_api.mock_query(response_file=response_file)

    # THEN progress should be returned
    assert tower_api.progress == expected_progress


def test_tower_api_tasks(
    tower_id: str,
    analysis_id: int,
    tower_task_response_running: Path,
    tower_jobs: List[dict],
) -> None:
    """Assess that TowerAPI returns a list of tasks given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(workflow_id=tower_id)
    tower_api.mock_tasks_query(response_file=tower_task_response_running)

    # WHEN asking for jobs
    jobs = tower_api.get_jobs(analysis_id=analysis_id)

    # THEN a list of jobs should be returned
    for job_nr in range(1, len(jobs)):
        assert dict(jobs[job_nr]) == dict(tower_jobs[job_nr])


def test_tower_api_tasks_empty(
    tower_id: str,
    analysis_id: int,
    tower_task_response_pending: Path,
) -> None:
    """Assess that TowerAPI returns an empty list of tasks given a response for a pending case."""

    # GIVEN an tower_api with a mock query response for a pending case
    tower_api = MockTowerAPI(workflow_id=tower_id)
    tower_api.mock_tasks_query(response_file=tower_task_response_pending)

    # WHEN asking for jobs
    jobs = tower_api.get_jobs(analysis_id=analysis_id)

    # THEN an empty list should be returned
    assert jobs == []


def test_tower_task_properties(
    tower_task: TowerTask,
    created_at,
    started_at,
    last_updated,
    tower_task_duration,
    slurm_id,
    tower_task_name,
) -> None:
    """Assess that TowerTask returns the right properties."""

    # GIVEN a tower task

    # THEN properties should be returned
    assert tower_task.process == tower_task_name
    assert tower_task.nativeId == slurm_id
    assert tower_task.status == TrailblazerStatus.COMPLETED.value
    assert tower_task.dateCreated == created_at
    assert tower_task.lastUpdated == last_updated
    assert tower_task.start == started_at
    assert tower_task.duration == tower_task_duration
    assert tower_task.is_complete is True
