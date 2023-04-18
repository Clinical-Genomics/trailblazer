import subprocess

from tests.apps.tower.conftest import TOWER_ID, CaseIDs, TowerResponseFile, TowerTaskResponseFile
from tests.mocks.tower_mock import MockTowerAPI
from trailblazer.store import Store


class MockStore(Store):
    """Instance of Store that mimics workflow manager outputs and interactions."""

    @staticmethod
    def query_slurm(job_id_file: str, case_id: str, ssh: bool) -> bytes:
        """Mock SLURM output."""
        slurm_dict = {
            "blazinginsect": "tests/fixtures/sacct/blazinginsect_sacct",  # running
            "crackpanda": "tests/fixtures/sacct/crackpanda_sacct",  # failed
            "daringpidgeon": "tests/fixtures/sacct/daringpidgeon_sacct",  # failed
            "emptydinosaur": "tests/fixtures/sacct/emptydinosaur_sacct",  # failed
            "escapedgoat": "tests/fixtures/sacct/escapegoat_sacct",  # pending
            "fancymole": "tests/fixtures/sacct/fancymole_sacct",  # completed
            "happycow": "tests/fixtures/sacct/happycow_sacct",  # pending
            "lateraligator": "tests/fixtures/sacct/lateraligator_sacct",  # failed
            "liberatedunicorn": "tests/fixtures/sacct/liberatedunicorn_sacct",  # error
            "nicemice": "tests/fixtures/sacct/nicemice_sacct",  # completed
            "rarekitten": "tests/fixtures/sacct/rarekitten_sacct",  # canceled
            "trueferret": "tests/fixtures/sacct/trueferret_sacct",  # running
        }
        return subprocess.check_output(["cat", slurm_dict.get(case_id)])

    @staticmethod
    def cancel_slurm_job(slurm_id: int, ssh: bool = False) -> None:
        return

    @staticmethod
    def query_tower(config_file: str, case_id: str) -> MockTowerAPI:
        """Return a mocked NF Tower API response."""
        configs = {
            CaseIDs.RUNNING: {
                "workflow_response_file": TowerResponseFile.RUNNING,
                "tasks_response_file": TowerTaskResponseFile.RUNNING,
                "tower_id": TOWER_ID,
                "analysis_id": 1,
            },
            CaseIDs.PENDING: {
                "workflow_response_file": TowerResponseFile.PENDING,
                "tasks_response_file": TowerTaskResponseFile.PENDING,
                "tower_id": TOWER_ID,
                "analysis_id": 1,
            },
            CaseIDs.COMPLETED: {
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
