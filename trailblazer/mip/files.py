"""Parse the MIP config, qc_metric and qc_sampleinfo file."""


PED_SEX_MAP = {1: "male", 2: "female", 0: "unknown"}


def parse_config(data: dict) -> dict:
    """Parse MIP config file.

    Args:
        data (dict): raw YAML input from MIP analysis config file

    Returns:
        dict: parsed data
    """
    return {
        "email": data.get("email"),
        "case": data["case_id"] if "case_id" in data else data["family_id"],  # family_id for MIP<7
        "samples": [
            {"id": sample_id, "type": analysis_type}
            for sample_id, analysis_type in data["analysis_type"].items()
        ],
        "config_path": data["config_file_analysis"],
        "is_dryrun": True if "dry_run_all" in data else False,
        "log_path": data["log_file"],
        "out_dir": data["outdata_dir"],
        "priority": data["slurm_quality_of_service"],
        "sampleinfo_path": data["sample_info_file"],
    }


def parse_sampleinfo_light(data: dict) -> dict:
    """Parse MIP sample info file and retrieve mip_version, date, and status

    Args:
        data (dict): raw YAML input from MIP qc sample info file

    Returns:
        dict: {'version': str, 'date': str, 'is_finished': str}

    """
    outdata = {
        "date": data["analysis_date"],
        "version": data["mip_version"],
        "is_finished": True if data["analysisrunstatus"] == "finished" else False,
    }

    return outdata


def get_sampleinfo_date(data: dict) -> str:
    """Get MIP sample info date.

    Args:
        data (dict): raw YAML input from MIP qc sample info file

    Returns:
        str: analysis date
    """

    return data["analysis_date"]


def get_rank_model_version(sample_info: dict, rank_model_type: str, step: str) -> str:
    """Get rank model version"""
    rank_model_version = None
    for key in ("recipe", "program"):
        if key in sample_info:
            rank_model_version = sample_info[key][step][rank_model_type]["version"]
            break
    return rank_model_version


def parse_sampleinfo(data: dict) -> dict:
    """Parse MIP sample info file.

    Args:
        data (dict): raw YAML input from MIP qc sample info file

    Returns:
        dict: parsed data
    """
    genome_build = data["human_genome_build"]
    genome_build_str = f"{genome_build['source']}{genome_build['version']}"
    outdata = {
        "date": data["analysis_date"],
        "genome_build": genome_build_str,
        "case": data["case"],
        "is_finished": True if data["analysisrunstatus"] == "finished" else False,
        "rank_model_version": get_rank_model_version(
            sample_info=data, rank_model_type="rank_model", step="genmod"
        ),
        "samples": [],
        "sv_rank_model_version": get_rank_model_version(
            sample_info=data, rank_model_type="sv_rank_model", step="sv_genmod"
        ),
        "version": data["mip_version"],
    }

    for sample_id in data["sample"].items():
        sample = {"id": sample_id}
        outdata["samples"].append(sample)

    return outdata


def get_plink_samples(metrics: dict) -> dict:
    """Get plink samples"""
    plink_sexcheck = None
    plink_samples = {}
    if "recipe" in metrics:
        plink_sexcheck = metrics["recipe"].get("plink_sexcheck", {}).get("sample_sexcheck")
    elif "program" in metrics:  # for MIP<7
        plink_sexcheck = metrics["program"].get("plink_sexcheck", {}).get("sample_sexcheck")
    if isinstance(plink_sexcheck, str):
        sample_id, sex_number = plink_sexcheck.strip().split(":", 1)
        plink_samples[sample_id] = PED_SEX_MAP.get(int(sex_number))
    elif isinstance(plink_sexcheck, list):
        for sample_raw in plink_sexcheck:
            sample_id, sex_number = sample_raw.split(":", 1)
            plink_samples[sample_id] = PED_SEX_MAP.get(int(sex_number))
    return plink_samples


def set_bamstats_metrics(file_metrics: dict, sample_data: dict) -> dict:
    """Set bamstats metrics"""
    total_reads = sample_data["reads"] if "reads" in sample_data else 0
    sample_data["reads"] = int(file_metrics["bamstats"]["raw_total_sequences"]) + total_reads

    total_mapped = sample_data["total_mapped"] if "total_mapped" in sample_data else 0
    sample_data["total_mapped"] = int(file_metrics["bamstats"]["reads_mapped"]) + total_mapped
    return sample_data


def set_chanjo_sexcheck_metrics(file_metrics: dict, sample_data: dict) -> dict:
    """Set chanjo_sexcheck metrics"""
    sample_data["predicted_sex"] = file_metrics["chanjo_sexcheck"]["gender"]
    return sample_data


def set_collecthsmetrics_metrics(file_metrics: dict, sample_data: dict) -> dict:
    """Set collecthsmetrics metrics"""
    hs_metrics = file_metrics["collecthsmetrics"]["header"]["data"]
    sample_data["at_dropout"] = float(hs_metrics["AT_DROPOUT"])
    sample_data["completeness_target"] = {
        10: float(hs_metrics["PCT_TARGET_BASES_10X"]),
        20: float(hs_metrics["PCT_TARGET_BASES_20X"]),
        50: float(hs_metrics["PCT_TARGET_BASES_50X"]),
        100: float(hs_metrics["PCT_TARGET_BASES_100X"]),
    }
    sample_data["gc_dropout"] = float(hs_metrics["GC_DROPOUT"])
    sample_data["target_coverage"] = float(hs_metrics["MEAN_TARGET_COVERAGE"])
    return sample_data


def set_collectmultiplemetrics_metrics(file_metrics: dict, sample_data: dict) -> dict:
    """Set collectmultiplemetrics metrics"""
    mm_metrics = file_metrics["collectmultiplemetrics"]["header"]["pair"]
    sample_data["strand_balance"] = float(mm_metrics["STRAND_BALANCE"])
    return sample_data


def set_collectmultiplemetricsinsertsize_metrics(file_metrics: dict, sample_data: dict) -> dict:
    """Set collectmultiplemetricsinsertsize metrics"""
    mm_insert_metrics = file_metrics["collectmultiplemetricsinsertsize"]["header"]["data"]
    sample_data["median_insert_size"] = int(mm_insert_metrics["MEDIAN_INSERT_SIZE"])
    sample_data["insert_size_standard_deviation"] = float(mm_insert_metrics["STANDARD_DEVIATION"])
    return sample_data


def set_markduplicates_metrics(file_metrics: dict, sample_data: dict) -> dict:
    """Set markduplicates metrics"""
    sample_data["duplicates"] = float(file_metrics["markduplicates"]["fraction_duplicates"])
    return sample_data


def get_sample_metrics(sample_metrics: dict, sample_data: dict) -> dict:
    """Get tool qc metrics from sample metrics"""
    get_metrics = {
        "bamstats": set_bamstats_metrics,
        "chanjo_sexcheck": set_chanjo_sexcheck_metrics,
        "collecthsmetrics": set_collecthsmetrics_metrics,
        "collectmultiplemetrics": set_collectmultiplemetrics_metrics,
        "collectmultiplemetricsinsertsize": set_collectmultiplemetricsinsertsize_metrics,
        "markduplicates": set_markduplicates_metrics,
    }

    for file_metrics in sample_metrics.values():

        for tool in file_metrics:

            if get_metrics.get(tool):
                get_metrics[tool](file_metrics=file_metrics, sample_data=sample_data)
    return sample_data


def parse_qcmetrics(metrics: dict) -> dict:
    """Parse MIP qc metrics file
    Args:
        metrics (dict): raw YAML input from MIP qc metrics file
    Returns:
        dict: parsed qc metrics metrics
    """
    qc_metric = {"samples": []}

    plink_samples = get_plink_samples(metrics=metrics)

    for sample_id, sample_metrics in metrics["sample"].items():

        sample_data = {"id": sample_id, "plink_sex": plink_samples.get(sample_id)}
        sample_data = get_sample_metrics(sample_metrics=sample_metrics, sample_data=sample_data)
        sample_data["mapped"] = sample_data["total_mapped"] / sample_data["reads"]
        qc_metric["samples"].append(sample_data)
    return qc_metric
