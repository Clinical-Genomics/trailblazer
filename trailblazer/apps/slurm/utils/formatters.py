from trailblazer.constants import Pipeline


def reformat_mip_job_step(job_step: str) -> str:
    """Reformat data analysis MIP job step.
    Raise: Exception if unable to split string.
    """
    try:
        return "_".join(job_step.split("_")[:-1])
    except Exception:
        return job_step


def reformat_balsamic_job_step(job_step: str) -> str:
    """Reformat data analysis Balsamic job step.
    Raise: Exception if unable to split string.
    """
    try:
        return job_step.split(".")[2]
    except Exception:
        return job_step


def reformat_mutant_job_step(job_step: str) -> str:
    """Reformat data analysis Mutant job step.
    Raise: Exception if unable to split string.
    """
    try:
        return job_step.split("_")[2]
    except Exception:
        return job_step


def reformat_undefined(job_step: str) -> str:
    """Reformat data analysis job step."""
    return job_step


formatter_map = {
    Pipeline.MIP_DNA: reformat_mip_job_step,
    Pipeline.MIP_RNA: reformat_mip_job_step,
    Pipeline.BALSAMIC: reformat_balsamic_job_step,
    Pipeline.SARS_COV_2: reformat_mutant_job_step,
}
