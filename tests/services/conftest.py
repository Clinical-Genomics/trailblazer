from unittest.mock import Mock
import pytest

from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.job_service.job_service import JobService
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.services.slurm.slurm_service import SlurmService
from trailblazer.store.store import Store


@pytest.fixture
def slurm_completed_job_info() -> SlurmJobInfo:
    return SlurmJobInfo(
        slurm_id=690994,
        name="job",
        status="completed",
        elapsed=1000,
        started_at="2020-10-22T11:43:33",
    )


@pytest.fixture
def slurm_service(slurm_completed_job_info) -> SlurmService:
    """Slurm service reporting all jobs as completed."""
    service = SlurmCLIService(client=Mock())
    service.get_job = Mock(return_value=slurm_completed_job_info)
    service.get_jobs = Mock(return_value=[slurm_completed_job_info])
    return service


@pytest.fixture
def job_service(store: Store, slurm_service: SlurmService, slurm_job_ids, mocker) -> JobService:
    mocker.patch(
        "trailblazer.services.job_service.job_service.get_slurm_job_ids", return_value=slurm_job_ids
    )
    return JobService(store=store, slurm_service=slurm_service)


@pytest.fixture
def analysis_service(analysis_store: Store, job_service: JobService) -> AnalysisService:
    return AnalysisService(store=analysis_store, job_service=job_service)
