from json import JSONDecodeError
from pathlib import Path

from trailblazer.apps.tower.api import TowerAPI
from trailblazer.apps.tower.models import TowerTaskResponse, TowerWorkflowResponse
from trailblazer.constants import FileFormat
from trailblazer.io.controller import ReadFile


class MockTowerAPI(TowerAPI):
    """Instance of TowerAPI that mimics expected Tower output."""

    @property
    def response(self) -> dict | None:
        return self.mock_response or None

    @property
    def tasks_response(self) -> dict | None:
        return self.mock_tasks_response or None

    def mock_query(self, response_file: Path) -> TowerWorkflowResponse:
        try:
            self.mock_response = TowerWorkflowResponse(
                **ReadFile.get_content_from_file(
                    file_format=FileFormat.JSON, file_path=response_file
                )
            )
        except JSONDecodeError:
            self.mock_response = TowerWorkflowResponse(**{})
        return self.mock_response

    def mock_tasks_query(self, response_file: Path) -> TowerTaskResponse:
        try:
            self.mock_tasks_response = TowerTaskResponse(
                **ReadFile.get_content_from_file(
                    file_format=FileFormat.JSON, file_path=response_file
                )
            )
        except JSONDecodeError:
            self.mock_tasks_response = TowerTaskResponse(**{})
        return self.mock_tasks_response
