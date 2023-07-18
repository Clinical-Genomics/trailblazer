import pytest

from trailblazer.apps.slurm.api import get_squeue_result, reformat_squeue_result_job_step
from trailblazer.apps.slurm.models import SqueueResult


def test_get_squeue_result(squeue_stream_jobs):
    # GIVEN a squeue stream

    # WHEN getting the squeue results
    squeue_result: SqueueResult = get_squeue_result(squeue_response=squeue_stream_jobs)

    # THEN it should return squeue jobs
    assert isinstance(squeue_result, SqueueResult)
    assert isinstance(squeue_result.jobs, list)


@pytest.mark.parametrize(
    "data_analysis, raw_job_step, expected_job_step",
    [
        ("MIP-DNA", "mipdnastep_jobstep", "mipdnastep"),
        ("MIP-RNA", "miprnastep_jobstep", "miprnastep"),
        ("BALSAMIC", "job.step.balsamicstep", "balsamicstep"),
        ("SARS-COV-2", "job_step_mutantstep", "mutantstep"),
    ],
)
def test_reformat_squeue_result_job_step(
    data_analysis: str, raw_job_step: str, expected_job_step: str
):
    # GIVEN a data analysis and a job step

    # WHEN reformation the job step
    reformatted_job_step: str = reformat_squeue_result_job_step(
        data_analysis=data_analysis, job_step=raw_job_step
    )

    # THEN it should return a reformatted job step
    assert reformatted_job_step == expected_job_step
