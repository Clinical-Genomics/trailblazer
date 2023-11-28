from datetime import datetime

from trailblazer.constants import SlurmJobStatus
from trailblazer.store.models import Analysis, Job, User


def test_user_first_name():
    """Test setting user first name."""
    # GIVEN a user with a name
    user: User = User(name="Paul T. Anderson")

    # WHEN accessing the first name
    first_name = user.first_name

    # THEN it should return the spoken name
    assert first_name == "Paul"


def test_analysis_most_recent_failed_job():
    """Test retrieving the most recent failed job."""
    # GIVEN an Analysis with several jobs, including failed ones
    analysis = Analysis(
        jobs=[
            Job(status=SlurmJobStatus.COMPLETED, started_at=datetime(2023, 1, 1)),
            Job(status=SlurmJobStatus.FAILED, started_at=datetime(2023, 1, 3)),
            Job(status=SlurmJobStatus.FAILED, started_at=datetime(2023, 1, 2)),
            Job(status=SlurmJobStatus.RUNNING, started_at=datetime(2023, 1, 4)),
        ]
    )

    # WHEN retrieving the most recent failed job
    most_recent_failed: Job | None = analysis.last_failed_job

    # THEN it should return the job with the status FAILED and the most recent started_at date
    assert most_recent_failed
    assert most_recent_failed.status == SlurmJobStatus.FAILED
    assert most_recent_failed.started_at == datetime(2023, 1, 3)


def test_get_analysis_non_existing_failed_job():
    """Test retrieving the most recent failed job, when none has failed."""
    # GIVEN an Analysis without any failed jobs
    analysis = Analysis(
        jobs=[Job(status=SlurmJobStatus.COMPLETED, started_at=datetime(2023, 1, 1))]
    )

    # WHEN retrieving the most recent failed job
    most_recent_failed: Job | None = analysis.last_failed_job

    # THEN it should not return any
    assert most_recent_failed


def test_get_analysis_most_recent_failed_job_when_no_jobs_exist():
    """Test retrieving the most recent failed job, when no jobs."""
    # GIVEN an Analysis without any jobs
    analysis = Analysis()

    # WHEN retrieving the most recent failed job
    most_recent_failed: Job | None = analysis.last_failed_job

    # THEN it should not return any
    assert most_recent_failed
