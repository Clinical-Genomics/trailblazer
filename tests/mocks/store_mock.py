from tests.apps.tower.conftest import TOWER_ID, CaseIDs, TowerResponseFile, TowerTaskResponseFile
from tests.mocks.tower_mock import MockTowerAPI
from trailblazer.store.api import Store


class MockStore(Store):
    """Instance of Store that mimics workflow manager outputs and interactions."""

    @staticmethod
    def query_slurm(job_id_file: str, case_id: str, ssh: bool) -> str:
        """Mock SLURM output."""
        slurm_dict = {
            "cuddlyhen": "tests/fixtures/sacct/blazinginsect_sacct_2",
            "blazinginsect": "tests/fixtures/sacct/blazinginsect_sacct_2",  # running
            "crackpanda": "tests/fixtures/sacct/crackpanda_sacct_2",  # failed
            "escapedgoat": "tests/fixtures/sacct/escapegoat_sacct_2",  # pending
            "fancymole": "tests/fixtures/sacct/fancymole_sacct_2",  # completed
            "happycow": "tests/fixtures/sacct/happycow_sacct_2",  # pending
            "lateraligator": "tests/fixtures/sacct/lateraligator_sacct_2",  # failed
            "nicemice": "tests/fixtures/sacct/nicemice_sacct_2",  # completed
            "rarekitten": "tests/fixtures/sacct/rarekitten_sacct_2",  # canceled
            "trueferret": "tests/fixtures/sacct/trueferret_sacct_2",  # running
        }
        with open(slurm_dict.get(case_id), "r") as file:
            file_content = file.read()
        return file_content

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
