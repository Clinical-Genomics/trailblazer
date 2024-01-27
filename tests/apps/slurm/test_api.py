import pytest

from trailblazer.apps.slurm.api import (
    _get_squeue_jobs_flag_input,
    get_current_analysis_status,
    get_squeue_result,
    reformat_squeue_result_job_step,
)
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.constants import Pipeline, SlurmJobStatus, TrailblazerStatus


def test_get_squeue_result(squeue_stream_jobs):
    # GIVEN a squeue stream

    # WHEN getting the squeue results
    squeue_result: SqueueResult = get_squeue_result(squeue_response=squeue_stream_jobs)

    # THEN it should return squeue results and jobs
    assert isinstance(squeue_result, SqueueResult)
    assert isinstance(squeue_result.jobs, list)


@pytest.mark.parametrize(
    "job_id, expected_job_id",
    [
        ({"a_case_with_ints": [1, 2]}, "1,2"),
        ({"a_case_with_quoted_ints": ["1", "2"]}, "1,2"),
    ],
)
def test_get_squeue_jobs_flag_input(job_id: dict[str, list[str]], expected_job_id: str):
    """Test return of squeue jobs flag formatted string."""
    # GIVEN a job ids

    # WHEN getting the squeue jobs flag input
    squeue_job_input: str = _get_squeue_jobs_flag_input(slurm_job_id_file_content=job_id)

    # THEN it should return job ids as comma joined string
    assert squeue_job_input == expected_job_id


@pytest.mark.parametrize(
    "data_analysis, raw_job_step, expected_job_step",
    [
        (Pipeline.MIP_DNA, "mipdnastep_jobstep", "mipdnastep"),
        (Pipeline.MIP_RNA, "miprnastep_jobstep", "miprnastep"),
        (Pipeline.BALSAMIC, "job.step.balsamicstep", "balsamicstep"),
        (Pipeline.SARS_COV_2, "job_step_mutantstep", "mutantstep"),
    ],
)
def test_reformat_squeue_result_job_step(
    data_analysis: str, raw_job_step: str, expected_job_step: str
):
    """Test reformatting job step name for each pipeline."""
    # GIVEN a data analysis and a job step

    # WHEN reformation the job step
    reformatted_job_step: str = reformat_squeue_result_job_step(
        data_analysis=data_analysis, job_step=raw_job_step
    )

    # THEN it should return a reformatted job step
    assert reformatted_job_step == expected_job_step


@pytest.mark.parametrize(
    "data_analysis, raw_job_step, expected_job_step",
    [
        (Pipeline.MIP_DNA, "jobstep", "jobstep"),
        (Pipeline.MIP_RNA, "jobstep", "jobstep"),
        (Pipeline.BALSAMIC, "job.step", "job.step"),
        (Pipeline.SARS_COV_2, "jobstep", "jobstep"),
    ],
)
def test_reformat_squeue_result_job_step_malformed_job_step(
    caplog, data_analysis: str, raw_job_step: str, expected_job_step: str
):
    """Test reformatting job step name for each pipeline when job step is malformed."""

    caplog.set_level("ERROR")
    # GIVEN a data analysis and a job step

    # WHEN reformation the job step
    reformatted_job_step: str = reformat_squeue_result_job_step(
        data_analysis=data_analysis, job_step=raw_job_step
    )

    # THEN it should return the original job step
    assert reformatted_job_step == expected_job_step
    assert f"Job step - {raw_job_step}: is malformed" in caplog.text


@pytest.mark.parametrize(
    "analysis_status, job_status_distribution, expected_analysis_status",
    [
        ("failed", {SlurmJobStatus.FAILED: 0.01}, TrailblazerStatus.FAILED),
        (
            "failed_ongoing",
            {SlurmJobStatus.FAILED: 0.01, SlurmJobStatus.RUNNING: 0.1},
            TrailblazerStatus.ERROR,
        ),
        ("error", {SlurmJobStatus.TIME_OUT: 0.01}, TrailblazerStatus.FAILED),
        (
            "error_ongoing",
            {SlurmJobStatus.TIME_OUT: 0.01, SlurmJobStatus.PENDING: 0.1},
            TrailblazerStatus.ERROR,
        ),
        ("completed", {SlurmJobStatus.COMPLETED: 1.0}, TrailblazerStatus.COMPLETED),
        ("pending", {SlurmJobStatus.PENDING: 1.0}, TrailblazerStatus.PENDING),
        (
            "running",
            {SlurmJobStatus.RUNNING: 0.01, SlurmJobStatus.PENDING: 0.1},
            TrailblazerStatus.RUNNING,
        ),
        ("canceled", {SlurmJobStatus.CANCELLED: 0.01}, TrailblazerStatus.CANCELLED),
        (
            "canceled_ongoing",
            {SlurmJobStatus.CANCELLED: 0.01, SlurmJobStatus.RUNNING: 0.1},
            TrailblazerStatus.RUNNING,
        ),
        (
            "canceled_ongoing_round_to_zero",
            {SlurmJobStatus.CANCELLED: 0.01, SlurmJobStatus.RUNNING: 0.00},
            TrailblazerStatus.RUNNING,
        ),
    ],
)
def test_get_current_analysis_status(
    analysis_status: str, job_status_distribution: dict[str, float], expected_analysis_status: str
):
    """Test return current analysis status from jobs status distribution."""
    # GIVEN a data analysis and a job status distribution

    # WHEN reformation the job step
    current_analysis_status: str | None = get_current_analysis_status(
        jobs_status_distribution=job_status_distribution
    )

    # THEN it should return the current job status distribution
    assert current_analysis_status == expected_analysis_status
