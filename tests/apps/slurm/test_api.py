from trailblazer.clients.slurm_cli_client.utils import get_squeue_result
from trailblazer.clients.slurm_cli_client.models import SqueueResult


def test_get_squeue_result(squeue_stream_jobs):
    # GIVEN a squeue stream

    # WHEN getting the squeue results
    squeue_result: SqueueResult = get_squeue_result(squeue_response=squeue_stream_jobs)

    # THEN it should return squeue results and jobs
    assert isinstance(squeue_result, SqueueResult)
    assert isinstance(squeue_result.jobs, list)
