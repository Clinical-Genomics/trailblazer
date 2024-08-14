from trailblazer.services.job_service import JobService
from trailblazer.store.models import Analysis


def test_job_progression_completed(job_service: JobService, analysis_with_completed_jobs: Analysis):
    # GIVEN an analysis with completed jobs

    # WHEN getting the analysis progression
    progression = job_service.get_analysis_progression(analysis_with_completed_jobs.id)

    # THEN the progression is 100%
    assert progression == 1.0


def test_job_progression_ongoing(job_service: JobService, analysis_with_running_jobs: Analysis):
    # GIVEN an analysis with ongoing jobs

    # WHEN getting the analysis progression
    progression = job_service.get_analysis_progression(analysis_with_running_jobs.id)

    # THEN the progression is less than 100%
    assert progression < 1.0
