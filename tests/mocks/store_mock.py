import subprocess
from pathlib import Path

from tests.apps.tower.conftest import TOWER_ID, CaseIDs, TowerResponseFile, TowerTaskResponseFile
from tests.mocks.tower_mock import MockTowerAPI
from trailblazer.constants import FileExtension
from trailblazer.store.api import Store


class MockStore(Store):
    """Instance of Store that mimics workflow manager outputs and interactions."""

    @staticmethod
    def query_slurm(job_id_file: str, case_id: str, ssh: bool) -> str:
        """Mock SLURM output."""
        slurm_dict = {
            "blazinginsect": Path(
                "tests", "fixtures", "squeue", "blazinginsect_squeue" + FileExtension.CSV
            ).as_posix(),
            "crackpanda": Path(
                "tests", "fixtures", "squeue", "crackpanda_squeue" + FileExtension.CSV
            ).as_posix(),
            "cuddlyhen": Path(
                "tests", "fixtures", "squeue", "cuddlyhen_squeue" + FileExtension.CSV
            ).as_posix(),
            "daringpidgeon": Path(
                "tests", "fixtures", "squeue", "daringpidgeon_squeue" + FileExtension.CSV
            ).as_posix(),
            "escapedgoat": Path(
                "tests", "fixtures", "squeue", "escapegoat_squeue" + FileExtension.CSV
            ).as_posix(),
            "fancymole": Path(
                "tests", "fixtures", "squeue", "fancymole_squeue" + FileExtension.CSV
            ).as_posix(),
            "happycow": Path(
                "tests", "fixtures", "squeue", "happycow_squeue" + FileExtension.CSV
            ).as_posix(),
            "lateraligator": Path(
                "tests", "fixtures", "squeue", "lateraligator_squeue" + FileExtension.CSV
            ).as_posix(),
            "nicemice": Path(
                "tests", "fixtures", "squeue", "nicemice_squeue" + FileExtension.CSV
            ).as_posix(),
            "rarekitten": Path(
                "tests", "fixtures", "squeue", "rarekitten_squeue" + FileExtension.CSV
            ).as_posix(),
            "trueferret": Path(
                "tests", "fixtures", "squeue", "trueferret_squeue" + FileExtension.CSV
            ).as_posix(),
        }

        return subprocess.check_output(["cat", slurm_dict.get(case_id)]).decode("utf-8")

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
