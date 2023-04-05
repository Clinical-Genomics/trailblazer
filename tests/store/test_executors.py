# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List

import pytest

from tests.conftest import JOB_LIST_PENDING, MockTowerAPI, TowerResponseFile, TowerTaskResponseFile
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.executors import TowerTask
from trailblazer.store.models import Job


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
    tower_api = MockTowerAPI(executor_id=tower_id)
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
def test_tower_api_is_pending(tower_id: str, response_file: Path, expected_bool: bool) -> None:
    """Assess that TowerAPI returns the state for is_pending given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(executor_id=tower_id)
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
def test_tower_api_total_jobs(tower_id: str, response_file: Path, expected_total_jobs: int) -> None:
    """Assess that TowerAPI correctly returns the total number jobs given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(executor_id=tower_id)
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
def test_tower_api_succeeded_jobs(
    tower_id: str, response_file: Path, expected_succeeded_jobs: int
) -> None:
    """Assess that TowerAPI correctly returns the number of succeeded jobs given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(executor_id=tower_id)
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
def test_tower_api_succeeded_jobs(
    tower_id: str, response_file: Path, expected_succeeded_jobs: int
) -> None:
    """Assess that TowerAPI correctly returns the number of succeeded jobs given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(executor_id=tower_id)
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
def test_tower_api_progress(tower_id: str, response_file: Path, expected_progress: int) -> None:
    """Assess that TowerAPI returns the progress percentage given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(executor_id=tower_id)
    tower_api.mock_query(response_file=response_file)

    # THEN total_jobs should be as expected according to the mocked response
    assert tower_api.progress == expected_progress


@pytest.mark.parametrize(
    "workflow_response_file, tasks_response_file, expected_jobs",
    [
        (TowerResponseFile.PENDING, TowerTaskResponseFile.PENDING, []),
        (TowerResponseFile.RUNNING, TowerTaskResponseFile.RUNNING, JOB_LIST_PENDING),
    ],
)
def test_tower_api_tasks(
    tower_id: str,
    analysis_id: str,
    workflow_response_file: Path,
    tasks_response_file: Path,
    expected_jobs: List[Job],
) -> None:
    """Assess that TowerAPI returns the progress percentage given a response."""

    # GIVEN an tower_api with a mock query response
    tower_api = MockTowerAPI(executor_id=tower_id)
    tower_api.mock_query(response_file=workflow_response_file)
    tower_api.mock_tasks_query(response_file=tasks_response_file)

    # THEN total_jobs should be as expected according to the mocked response
    jobs = tower_api.get_jobs(analysis_id=analysis_id)
    if not expected_jobs:
        assert jobs == expected_jobs
    else:
        assert (dict(jobs[i]) == dict(expected_jobs[i]) for i in range(1, len(jobs)))


def test_tower_task_properties(tower_task: TowerTask) -> None:
    """Assess that TowerTask returns the right properties."""

    # GIVEN a tower task

    # THEN properties should be as expected
    assert tower_task.name == "NFCORE_RNAFUSION:RNAFUSION:INPUT_CHECK:SAMPLESHEET_CHECK"
    assert tower_task.slurm_id == "4611827"
    assert tower_task.status == TrailblazerStatus.COMPLETED.value
    assert tower_task.date_created == "2023-04-04T08:11:24Z"
    assert tower_task.last_updated == "2023-04-04T08:11:28Z"
    assert tower_task.start == "2023-04-04T08:11:27Z"
    assert tower_task.duration == 3798
    assert tower_task.is_complete == True
