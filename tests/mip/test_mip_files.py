# -*- coding: utf-8 -*-
from trailblazer.mip import files


def test_parse_config(files_raw):
    # GIVEN config data of a "sharp" run (not dry run)
    config_raw = files_raw['config']
    # WHEN parsing the MIP output config
    config_data = files.parse_config(config_raw)
    # THEN it should work and the dry run check should be "no"
    assert config_data['is_dryrun'] is False
    # ... and should include all samples
    assert len(config_raw['analysis_type']) == len(config_data['samples'])


def test_parse_sampleinfo(files_raw):
    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw['sampleinfo']
    # WHEN parsing the MIP output sampleinfo
    sampleinfo_data = files.parse_sampleinfo(sampleinfo_raw)
    # THEN it should mark the run as "finished"
    assert sampleinfo_data['is_finished'] is True
    # ... and the genome build string should be assembled correctly
    assert sampleinfo_data['genome_build'] == 'GRCh37'


def test_parse_qcmetrics(files_raw):
    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw['qcmetrics']
    # WHEN parsing it
    qcmetrics_data = files.parse_qcmetrics(qcmetrics_raw)
    # THEN it should work ;-)
    assert isinstance(qcmetrics_data, dict)
