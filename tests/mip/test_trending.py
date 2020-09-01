# -*- coding: utf-8 -*-
"""Test MIP files"""

from trailblazer.mip import trending


def test_parse_mip_analysis(files_raw) -> dict:
    """
    Args:
    files_raw (dict): With dicts from files
    """
    # GIVEN config data of a "sharp" run (not dry run)
    mip_config_raw = files_raw["config"]

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw["sampleinfo"]

    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw["qcmetrics"]

    trend_data = trending.parse_mip_analysis(
        mip_config_raw, qcmetrics_raw, sampleinfo_raw
    )

    # Build dict for family return data
    trend_test_data = {
        "case": "case",
        "genome_build": "grch37",
        "mip_version": "v7.1.0",
        "rank_model_version": "1.25",
    }

    # Check returns from def
    for key, value in trend_test_data.items():
        assert trend_data[key] == value

    # Check sample id
    assert "mother" in trend_data["sample_ids"]

    # Build dict for sample return data
    trend_test_sample_data = {
        "at_dropout": {
            "mother": 1.716704,
        },
        "analysis_sex": {
            "mother": "female",
        },
        "duplicates": {
            "mother": 3.7952329122913104,
        },
        "insert_size_standard_deviation": {
            "mother": 94.353778,
        },
        "mapped_reads": {
            "mother": 99.74176575073072,
        },
        "median_insert_size": {
            "mother": 409,
        },
        "gc_dropout": {
            "mother": 0.214813,
        },
    }

    # Check returns from def
    for metric in trend_test_sample_data:
        for sample, value in trend_test_sample_data[metric].items():
            assert trend_data[metric][sample] == value
