# -*- coding: utf-8 -*-
"""Test MIP files"""

from trailblazer.mip import trending


def test_parse_mip_analysis(files_raw) -> dict:
    """
    Args:
    files_raw (dict): With dicts from files
    """
    # GIVEN config data of a "sharp" run (not dry run)
    mip_config_raw = files_raw['config']

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw['sampleinfo']

    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw['qcmetrics']

    trend_data = trending.parse_mip_analysis(mip_config_raw, qcmetrics_raw, sampleinfo_raw)

    ## Build dict for family return data
    trend_test_data = {
        'family': 'family',
        'genome_build': 'GRCh37',
        'mip_version': 'v6.0.0',
        'rank_model_version': '1.20'
    }

    # Check returns from def
    for key, value in trend_test_data.items():
        assert trend_data[key] == value

    ## Check sample id
    assert 'sample' in trend_data['sample_ids']

    ## Build dict for sample return data
    trend_test_sample_data = {
        'at_dropout': {
            'sample': 0.126963,
            },
        'analysis_sex': {
            'sample': 'female',
            },
        'duplicates': {
            'sample': 13.2719986683768,
            },
        'insert_size_standard_deviation': {
            'sample': 89.871783,
            },
        'mapped_reads': {
            'sample': 98.50732625744484,
            },
        'median_insert_size': {
            'sample': 413,
            },
        'gc_dropout': {
            'sample': 3.956909,
            },
    }

    # Check returns from def
    for metric in trend_test_sample_data:
        for sample, value in trend_test_sample_data[metric].items():
            assert trend_data[metric][sample] == value
