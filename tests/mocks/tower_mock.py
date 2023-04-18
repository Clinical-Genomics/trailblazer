from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional

from trailblazer.apps.tower.api import TowerAPI
from trailblazer.apps.tower.models import TowerTaskResponse, TowerWorkflowResponse
from trailblazer.io.json import read_json


class MockTowerAPI(TowerAPI):
    """Instance of TowerAPI that mimics expected Tower output."""

    @property
    def response(self) -> Optional[dict]:
        return self.mock_response or None

    @property
    def tasks_response(self) -> Optional[dict]:
        return self.mock_tasks_response or None

    def mock_query(self, response_file: Path) -> TowerWorkflowResponse:
        try:
            self.mock_response = TowerWorkflowResponse(**read_json(response_file))
        except JSONDecodeError:
            self.mock_response = TowerWorkflowResponse(**{})
        return self.mock_response

    def mock_tasks_query(self, response_file: Path) -> TowerTaskResponse:
        try:
            self.mock_tasks_response = TowerTaskResponse(**read_json(response_file))
        except JSONDecodeError:
            self.mock_tasks_response = TowerTaskResponse(**{})
        return self.mock_tasks_response
