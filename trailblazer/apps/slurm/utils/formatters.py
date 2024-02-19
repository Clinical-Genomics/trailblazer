import logging
from typing import Callable

from trailblazer.constants import Workflow

LOG = logging.getLogger(__name__)


def reformat_mip_job_step(job_step: str) -> str:
    """Reformat data analysis MIP job step."""
    reformatted_job_step: str = "_".join(job_step.split("_")[:-1])
    if reformatted_job_step:
        return reformatted_job_step
    else:
        LOG.error(f"Job step - {job_step}: is malformed")
        return job_step


def reformat_balsamic_job_step(job_step: str) -> str:
    """Reformat data analysis Balsamic job step.
    Raise: IndexError if unable to split string.
    """
    try:
        return job_step.split(".")[2]
    except IndexError as error:
        LOG.error(f"Job step - {job_step}: is malformed. {error}")
        return job_step


def reformat_mutant_job_step(job_step: str) -> str:
    """Reformat data analysis Mutant job step.
    Raise: IndexError if unable to split string.
    """
    try:
        return job_step.split("_")[2]
    except IndexError as error:
        LOG.error(f"Job step - {job_step}: is malformed. {error}")
        return job_step


def reformat_undefined(job_step: str) -> str:
    """Reformat data analysis job step."""
    return job_step


formatter_map: dict[str, Callable] = {
    Workflow.MIP_DNA: reformat_mip_job_step,
    Workflow.MIP_RNA: reformat_mip_job_step,
    Workflow.BALSAMIC: reformat_balsamic_job_step,
    Workflow.MUTANT: reformat_mutant_job_step,
}
