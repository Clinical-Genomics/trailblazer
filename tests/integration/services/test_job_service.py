from unittest import mock
from trailblazer.constants import SlurmJobStatus
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.store.models import Analysis


def test_update_upload_jobs(
    job_service: JobService, upload_job_info: SlurmJobInfo, analysis: Analysis
):
    # GIVEN a store with an analysis with an ongoing upload job

    # GIVEN that slurm says the upload job is completed
    slurm_service_mock = mock.Mock()
    slurm_service_mock.get_job.return_value = upload_job_info
    job_service.slurm_service = slurm_service_mock

    # WHEN updating the upload jobs
    job_service.update_upload_jobs()

    # THEN the upload job is marked as completed
    analysis: Analysis = job_service.store.get_analysis_with_id(analysis.id)
    assert analysis.upload_jobs
    assert analysis.upload_jobs[0].status == SlurmJobStatus.COMPLETED
