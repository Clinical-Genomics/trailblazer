def transform_mip_job_name(job_name: str) -> str:
    return "_".join(job_name.split("_")[:-1])


def transform_balsamic_job_name(job_name: str) -> str:
    return job_name.split(".")[2]


def transform_undefined(job_name: str) -> str:
    return job_name


formatter_map = {
    "MIP-DNA": transform_mip_job_name,
    "MIP-RNA": transform_mip_job_name,
    "BALSAMIC": transform_balsamic_job_name,
}
