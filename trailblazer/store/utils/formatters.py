def transform_mip_job_name(job_name: str) -> str:
    try:

        return "_".join(job_name.split("_")[:-1])
    except Exception:
        return job_name


def transform_balsamic_job_name(job_name: str) -> str:
    try:
        return job_name.split(".")[2]
    except Exception:
        return job_name


def transform_mutant_job_name(job_name: str) -> str:
    try:
        return job_name.split("_")[2]
    except Exception:
        return job_name


def transform_undefined(job_name: str) -> str:
    return job_name


formatter_map = {
    "MIP-DNA": transform_mip_job_name,
    "MIP-RNA": transform_mip_job_name,
    "BALSAMIC": transform_balsamic_job_name,
    "SARS-COV-2": transform_mutant_job_name,
}
