"""Test MIP files"""

import copy
import dateutil
import pytest

from trailblazer.mip import files


@pytest.mark.parametrize(
    "config, expected_case",
    [
        ({"case_id": "crazygoat"}, "crazygoat"),
        ({"family_id": "crazygoat"}, "crazygoat"),
        ({"not_a_case_id": "anonymous"}, None),
    ],
)
def test_get_case_from_config(config: dict, expected_case: str):
    """Test getting the case id from mip config"""
    # GIVEN a case id or family id

    # WHEN getting case from config dict
    case = files.get_case_from_config(config=config)

    # THEN return case
    assert case == expected_case


@pytest.mark.parametrize(
    "config, expected_bool",
    [
        ({"dry_run_all": 1}, True),
        ({"not_a_dry_run": 1}, False),
    ],
)
def test_get_dry_run_all(config: dict, expected_bool: bool):
    """Test getting the dry_run_all from mip config"""
    # GIVEN a dry run mip analysis

    # WHEN getting dry_run_all from config dict
    is_dry_run = files.get_dry_run_all(config=config)

    # THEN return true
    assert is_dry_run == expected_bool


def test_get_sample_data_from_config():
    """Test getting sample data from mip config"""
    # GIVEN sample data from a mip analysis config
    config = {
        "analysis_type": {"sample_1": "wgs"},
    }

    # WHEN getting sample data from config dict
    sample_data = files.get_sample_data_from_config(config=config)

    expected_sample_data = [
        {
            "id": "sample_1",
            "type": "wgs",
        }
    ]
    # THEN return true
    assert sample_data == expected_sample_data


def test_parse_config(files_raw: dict) -> dict:
    """
    Args:
    files_raw (dict): With dicts from files
    """

    # GIVEN config data of a "sharp" run (not dry run)
    config_raw = files_raw["config"]

    # WHEN parsing the MIP output config
    config_data = files.parse_config(config_raw)

    # THEN it return a dict
    assert isinstance(config_data, dict)

    # THEN the dry run is True
    assert config_data["is_dryrun"] is True

    # THEN the number of samples and analysis_types should be equal
    assert len(config_raw["analysis_type"]) == len(config_data["samples"])

    expected_config_data = {
        "case": "case",
        "config_path": "/path_to/cases/case/analysis/case_config.yaml",
        "is_dryrun": True,
        "email": "test.person@test.se",
        "log_path": "tests/fixtures/case/mip_2019-07-04T10:47:15.log",
        "out_dir": "/path_to/cases/case/analysis",
        "priority": "normal",
        "sampleinfo_path": "/path_to/cases/case/analysis/case_qc_sample_info.yaml",
    }

    # Then config data should be set
    for key, value in expected_config_data.items():
        assert config_data[key] == value


@pytest.mark.parametrize(
    "sample_info, expected_bool",
    [
        (
            {
                "analysisrunstatus": "finished",
            },
            True,
        ),
        (
            {
                "analysisrunstatus": "notfinished",
            },
            False,
        ),
    ],
)
def test_get_analysisrunstatus(sample_info: dict, expected_bool: bool):
    """Test getting analysis run status from mip config"""
    # GIVEN a run status from a sample_info file

    # WHEN getting sample data from config dict
    is_finished = files.get_analysisrunstatus(sample_info=sample_info)

    # THEN return true
    assert is_finished == expected_bool


def test_get_sampleinfo_date():
    """Test getting the case id from mip config"""
    # GIVEN a date
    sample_info = {
        "analysis_date": "1999-12-31",
    }

    # WHEN getting date from sample info
    date = files.get_sampleinfo_date(data=sample_info)

    # THEN return analysis date
    assert date == "1999-12-31"


def test_parse_sampleinfo_light(files_raw: dict):
    """
    Args:
    files_raw (dict): With dicts from files
    """

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw["sampleinfo"]

    # WHEN parsing the MIP output sampleinfo
    sampleinfo_data = files.parse_sampleinfo_light(sampleinfo_raw)

    # THEN it should return a dict
    assert isinstance(sampleinfo_data, dict)

    # THEN is_finished should be true
    assert sampleinfo_data["is_finished"] is True

    # THEN date should be set
    assert sampleinfo_data["date"] == dateutil.parser.parse("2019-07-05T10:12:03")

    # THEN version should be set
    assert sampleinfo_data["version"] == "v7.1.0"


def test_get_rank_model_version(files_raw: dict, mip_meta_data: dict):
    """Test getting the rank model from sample_info file"""

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw["sampleinfo"]

    # WHEN getting the rank_model
    rank_model_version = files.get_rank_model_version(
        sample_info=sampleinfo_raw, rank_model_type="rank_model", step="genmod"
    )

    # THEN the rank model version should be returned
    assert rank_model_version == mip_meta_data["RANK_MODEL_VERSION"]


def test_get_rank_model_version_with_program(files_raw: dict, mip_meta_data: dict):
    """Test getting the rank model from sample_info file with program key"""

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = copy.copy(files_raw["sampleinfo"])

    # Using old MIP style with program instead of recipe
    sampleinfo_raw["program"] = sampleinfo_raw.pop("recipe")

    # WHEN getting the rank_model
    rank_model_version = files.get_rank_model_version(
        sample_info=sampleinfo_raw, rank_model_type="rank_model", step="genmod"
    )

    # THEN the rank model version should be returned
    assert rank_model_version == mip_meta_data["RANK_MODEL_VERSION"]


@pytest.mark.parametrize(
    "sample_info, expected_case",
    [
        ({"case": "crazygoat"}, "crazygoat"),
        ({"family": "crazygoat"}, "crazygoat"),
        ({"not_a_case": "anonymous"}, None),
    ],
)
def test_get_case_from_sampleinfo(sample_info: dict, expected_case: str):
    """Test getting the case or family from mip sampleinfo file"""
    # GIVEN a case or family

    # WHEN getting case from config dict
    case = files.get_case_from_sampleinfo(sample_info=sample_info)

    # THEN return case
    assert case == expected_case


def test_get_genome_build(mip_meta_data: dict):
    """Test getting sample data from mip config"""
    # GIVEN human genome build in sample info
    sample_info = {
        "human_genome_build": {
            "source": mip_meta_data["GENOME_BUILD_SOURCE"],
            "version": mip_meta_data["GENOME_BUILD_VERSION"],
        },
    }

    # WHEN getting sample data from config dict
    genome_build = files.get_genome_build(sample_info=sample_info)

    # THEN return genome build (source and version)
    assert genome_build == "grch37"


def test_parse_sampleinfo(files_raw: dict, mip_meta_data: dict):
    """
    Args:
    files_raw (dict): With dicts from files
    """

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw["sampleinfo"]

    # WHEN parsing the MIP output sampleinfo
    sampleinfo_data = files.parse_sampleinfo(sampleinfo_raw)

    # THEN it should return a dict
    assert isinstance(sampleinfo_data, dict)

    # THEN is_finished should be True
    assert sampleinfo_data["is_finished"] is True

    expected_sampleinfo_data = {
        "case": "case",
        "genome_build": "grch37",
        "version": "v7.1.0",
    }

    # Then sampleinfo case data should be set
    for key, value in expected_sampleinfo_data.items():
        assert sampleinfo_data[key] == value

    expected_sampleinfo_sample_data = {"id": "mother"}

    # Then sampleinfo sample data should be set
    for key, value in expected_sampleinfo_sample_data.items():
        for sample_data in sampleinfo_data["samples"]:

            if sample_data["id"] != expected_sampleinfo_sample_data["id"]:
                continue

            assert sample_data[key] == value

    # THEN the number of samples and analysis_types should be equal
    assert len(sampleinfo_raw["analysis_type"]) == len(sampleinfo_data["samples"])


def test_set_bamstats_metrics_single_bamstat():
    """Test setting bam stats from qc_metrics when single bamstat entry"""
    # GIVEN 2 bamstats file metrics for a sample
    file_metric = {"bamstats": {"raw_total_sequences": 2, "reads_mapped": 1}}
    sample_data = {}

    # WHEN setting bamstats metrics
    sample_data = files.set_bamstats_metrics(
        file_metrics=file_metric, sample_data=sample_data
    )

    expected_sample_data = {"reads": 2, "total_mapped": 1}
    # THEN return bam stats metrics in sample data for file metric
    assert sample_data == expected_sample_data


def test_set_bamstats_metrics_mutiple_bamstat():
    """Test setting bam stats from qc_metrics when multiple bamstat entry"""
    # GIVEN 2 bamstats file metrics for a sample
    sample_metric = {
        "file_1": {"bamstats": {"raw_total_sequences": 2, "reads_mapped": 1}},
        "file_2": {"bamstats": {"raw_total_sequences": 1, "reads_mapped": 2}},
    }
    sample_data = {}

    for file_metric in sample_metric:
        # WHEN setting bamstats metrics
        sample_data = files.set_bamstats_metrics(
            file_metrics=sample_metric[file_metric], sample_data=sample_data
        )

    expected_sample_data = {"reads": 3, "total_mapped": 3}
    # THEN return bam stats metrics in sample data for file metric
    assert sample_data == expected_sample_data


def test_set_chanjo_sexcheck_metrics(files_raw: dict):
    """Test setting gender from file metric for chanjo_sexcheck"""
    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw["qcmetrics"]

    # Isolating to a single file_metric i.e. markduplicates
    sample_metrics = qcmetrics_raw["sample"]["father"][
        "father_lanes_1_sorted_md_brecal_sex"
    ]
    sample_data = {}

    # WHEN setting sample metric for file
    sample_data = files.set_chanjo_sexcheck_metrics(
        file_metrics=sample_metrics, sample_data=sample_data
    )

    expected_sample_data = {"predicted_sex": "male"}
    # THEN return predicted sex in sample data for file metric
    assert sample_data == expected_sample_data


def test_set_collecthsmetrics_metrics(files_raw: dict, mip_meta_data: dict):
    """Test setting hsmetrics metrics from file metric for collecthsmetrics"""
    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw["qcmetrics"]

    # Isolating to a single file_metric i.e. markduplicates
    sample_metrics = qcmetrics_raw["sample"]["father"][
        "father_lanes_1_sorted_md_brecal_collecthsmetrics"
    ]
    sample_data = {}

    # WHEN setting sample metric for file
    sample_data = files.set_collecthsmetrics_metrics(
        file_metrics=sample_metrics, sample_data=sample_data
    )

    expected_sample_data = {
        "at_dropout": mip_meta_data["FATHER_AT_DROPOUT"],
        "completeness_target": {
            10: mip_meta_data["FATHER_PCT_TARGET_BASES_10X"],
            20: mip_meta_data["FATHER_PCT_TARGET_BASES_20X"],
            50: mip_meta_data["FATHER_PCT_TARGET_BASES_50X"],
            100: mip_meta_data["FATHER_PCT_TARGET_BASES_100X"],
        },
        "gc_dropout": mip_meta_data["FATHER_GC_DROPOUT"],
        "target_coverage": mip_meta_data["FATHER_MEAN_TARGET_COVERAGE"],
    }
    # THEN return hs metrics in sample data for file metric
    assert sample_data == expected_sample_data


def test_set_collectmultiplemetrics_metrics(files_raw: dict, mip_meta_data: dict):
    """Test setting multiple metrics from file metric for collectmultiplemetrics"""
    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw["qcmetrics"]

    # Isolating to a single file_metric i.e. collectmultiplemetrics
    sample_metrics = qcmetrics_raw["sample"]["father"][
        "father_lanes_1_sorted_md_brecal_collectmultiplemetrics"
    ]
    sample_data = {}

    # WHEN setting sample metric for file
    sample_data = files.set_collectmultiplemetrics_metrics(
        file_metrics=sample_metrics, sample_data=sample_data
    )

    expected_sample_data = {"strand_balance": mip_meta_data["FATHER_STRAND_BALANCE"]}
    # THEN return strand balance in sample data for file metric
    assert sample_data == expected_sample_data


def test_set_collectmultiplemetricsinsertsize_metrics(
    files_raw: dict, mip_meta_data: dict
):
    """Test setting multiple metrics from file metric for collectmultiplemetricsinsertsize"""
    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw["qcmetrics"]

    # Isolating to a single file_metric i.e. collectmultiplemetricsinsertsize
    sample_metrics = qcmetrics_raw["sample"]["father"][
        "father_lanes_1_sorted_md_brecal_collectmultiplemetrics"
    ]
    sample_data = {}

    # WHEN setting sample metric for file
    sample_data = files.set_collectmultiplemetricsinsertsize_metrics(
        file_metrics=sample_metrics, sample_data=sample_data
    )

    expected_sample_data = {
        "median_insert_size": mip_meta_data["FATHER_MEDIAN_INSERT_SIZE"],
        "insert_size_standard_deviation": mip_meta_data["FATHER_STANDARD_DEVIATION"],
    }
    # THEN return insert size metrics in sample data for file metric
    assert sample_data == expected_sample_data


def test_set_markduplicates_metrics(files_raw: dict, mip_meta_data: dict):
    """Test setting duplicates metrics from file metric for markduplicates"""
    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw["qcmetrics"]

    # Isolating to a single file_metric i.e. markduplicates
    sample_metrics = qcmetrics_raw["sample"]["father"]["father_lanes_1_sorted_md"]
    sample_data = {}

    # WHEN setting sample metric for file
    sample_data = files.set_markduplicates_metrics(
        file_metrics=sample_metrics, sample_data=sample_data
    )

    expected_sample_data = {"duplicates": mip_meta_data["FATHER_FRACTION_DUPLICATES"]}
    # THEN return duplicates in sample data for file metric
    assert sample_data == expected_sample_data


def test_get_sample_metrics(files_raw: dict, mip_meta_data: dict):
    """Test getting sample data for duplicates from file metrics for markduplicates"""
    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw["qcmetrics"]

    # Isolating to a single file_metric i.e. markduplicates
    sample_metrics = {
        "father_lanes_1_sorted_md": qcmetrics_raw["sample"]["father"][
            "father_lanes_1_sorted_md"
        ]
    }
    sample_data = {}

    # WHEN getting sample metric for file
    sample_data = files.get_sample_metrics(
        sample_metrics=sample_metrics, sample_data=sample_data
    )

    expected_sample_data = {"duplicates": mip_meta_data["FATHER_FRACTION_DUPLICATES"]}
    # THEN return duplicates in sample data for file metric
    assert sample_data == expected_sample_data


def test_parse_qcmetrics(files_raw: dict, mip_meta_data: dict):
    """
    Args:
    files_raw (dict): With dicts from files
    """

    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw["qcmetrics"]

    # WHEN parsing qc metric data
    qcmetrics_data = files.parse_qcmetrics(qcmetrics_raw)

    # THEN it should return a dict
    assert isinstance(qcmetrics_data, dict)

    # Sample data
    # Build dict for sample return data
    expected_qcmetrics_sample_data = {
        "at_dropout": mip_meta_data["MOTHER_AT_DROPOUT"],
        "duplicates": mip_meta_data["MOTHER_FRACTION_DUPLICATES"],
        "id": "mother",
        "insert_size_standard_deviation": mip_meta_data["MOTHER_STANDARD_DEVIATION"],
        "gc_dropout": mip_meta_data["MOTHER_GC_DROPOUT"],
        "mapped": mip_meta_data["MOTHER_MAPPED"],
        "median_insert_size": mip_meta_data["MOTHER_MEDIAN_INSERT_SIZE"],
        "predicted_sex": "female",
        "reads": mip_meta_data["MOTHER_RAW_TOTAL_SEQUENCES"],
        "strand_balance": mip_meta_data["MOTHER_STRAND_BALANCE"],
        "target_coverage": mip_meta_data["MOTHER_MEAN_TARGET_COVERAGE"],
    }

    # THEN qcmetrics sample metrics should be set
    for key, value in expected_qcmetrics_sample_data.items():
        for sample_data in qcmetrics_data["samples"]:

            if sample_data["id"] != expected_qcmetrics_sample_data["id"]:
                continue

            assert sample_data[key] == value

    expected_qcmetrics_sample_cov_data = {
        10: mip_meta_data["MOTHER_PCT_TARGET_BASES_10X"],
        20: mip_meta_data["MOTHER_PCT_TARGET_BASES_20X"],
        50: mip_meta_data["MOTHER_PCT_TARGET_BASES_50X"],
        100: mip_meta_data["MOTHER_PCT_TARGET_BASES_100X"],
    }

    # THEN qcmetrics sample coverage metrics should be set
    for key, value in expected_qcmetrics_sample_cov_data.items():
        for sample_data in qcmetrics_data["samples"]:

            if sample_data["id"] != expected_qcmetrics_sample_data["id"]:
                continue

            assert sample_data["completeness_target"][key] == value
