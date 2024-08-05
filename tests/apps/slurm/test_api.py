import pytest

from trailblazer.apps.slurm.api import (
    _get_squeue_jobs_flag_input,
    get_squeue_result,
)
from trailblazer.apps.slurm.models import SqueueResult

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
