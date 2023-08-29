from tests.apps.tower.conftest import (
    TOWER_ID,
    CaseName,
    TowerResponseFile,
    TowerTaskResponseFile,
)
from tests.mocks.tower_mock import MockTowerAPI
from trailblazer.store.api import Store


class MockStore(Store):
    """Instance of Store that mimics workflow manager outputs and interactions."""

    @staticmethod
    def cancel_slurm_job(slurm_id: int, ssh: bool = False) -> None:
        return

    @staticmethod
    def query_tower(config_file: str, case_id: str) -> MockTowerAPI:
        """Return a mocked NF Tower API response."""
        configs = {
            CaseName.RUNNING: {
                "workflow_response_file": TowerResponseFile.RUNNING,
                "tasks_response_file": TowerTaskResponseFile.RUNNING,
                "tower_id": TOWER_ID,
                "analysis_id": 1,
            },
            CaseName.PENDING: {
                "workflow_response_file": TowerResponseFile.PENDING,
                "tasks_response_file": TowerTaskResponseFile.PENDING,
                "tower_id": TOWER_ID,
                "analysis_id": 1,
            },
            CaseName.COMPLETED: {
                "workflow_response_file": TowerResponseFile.COMPLETED,
                "tasks_response_file": TowerTaskResponseFile.COMPLETED,
                "tower_id": TOWER_ID,
                "analysis_id": 1,
            },
        }
        case = configs.get(case_id)
        tower_api = MockTowerAPI(workflow_id=case.get("tower_id"))
        tower_api.mock_query(response_file=case.get("workflow_response_file"))
        tower_api.mock_tasks_query(response_file=case.get("tasks_response_file"))
        return tower_api
