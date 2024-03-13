import pytest

from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.store import Store


@pytest.fixture
def analysis_service(analysis_store: Store) -> AnalysisService:
    return AnalysisService(analysis_store)
