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
    "MIP-DNA": reformat_mip_job_step,
    "MIP-RNA": reformat_mip_job_step,
    "BALSAMIC": reformat_balsamic_job_step,
    "SARS-COV-2": reformat_mutant_job_step,
}
