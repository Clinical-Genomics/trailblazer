from json import JSONDecodeError
from pathlib import Path
from typing import Any

from trailblazer.io.json import read_json
from trailblazer.store.utils.executors import TowerAPI
from trailblazer.store.utils.tower import TowerWorkflowResponse


class MockTowerAPI(TowerAPI):
    """Instance of TowerAPI that mimics expected Tower output."""

    @property
    def response(self) -> dict:
        return self.mock_response or None

    @property
    def tasks_response(self) -> dict:
        return self.mock_tasks_response or None

    def mock_query(self, response_file: Path) -> Any:
        try:
            self.mock_response = TowerWorkflowResponse(**read_json(response_file))
        except JSONDecodeError:
            self.mock_response = TowerWorkflowResponse(**{})
        return self.mock_response

    def mock_tasks_query(self, response_file: Path) -> Any:
        try:
            self.mock_tasks_response = read_json(response_file)
        except JSONDecodeError:
            self.mock_tasks_response = {}
        return self.mock_tasks_response
