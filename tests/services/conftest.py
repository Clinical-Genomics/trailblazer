from unittest.mock import Mock
import pytest

from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.job_service.job_service import JobService
from trailblazer.store.store import Store


@pytest.fixture
def job_service(store: Store) -> JobService:
    return JobService(store=store, slurm_service=Mock())


@pytest.fixture
def analysis_service(analysis_store: Store, job_service: JobService) -> AnalysisService:
    return AnalysisService(store=analysis_store, job_service=job_service)
