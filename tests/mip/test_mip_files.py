"""Test MIP files"""

import copy
import dateutil

from trailblazer.mip import files

RANK_MODEL_VERSION = '1.25'

def test_parse_config(files_raw) -> dict:
    """
    Args:
    files_raw (dict): With dicts from files
    """

    # GIVEN config data of a "sharp" run (not dry run)
    config_raw = files_raw['config']

    # WHEN parsing the MIP output config
    config_data = files.parse_config(config_raw)

    # THEN it should work
    assert isinstance(config_data, dict)

    # THEN it should work and the dry run check should be "yes"
    assert config_data['is_dryrun'] is True

    # ... and should include all samples
    assert len(config_raw['analysis_type']) == len(config_data['samples'])

    # Build dict for return data
    config_test_data = {
        'config_path': '/path_to/cases/case/analysis/case_config.yaml',
        'email': 'test.person@test.se',
        'case': 'case',
        'log_path': 'tests/fixtures/case/mip_2019-07-04T10:47:15.log',
        'sampleinfo_path': '/path_to/cases/case/analysis/case_qc_sample_info.yaml',
        'out_dir': '/path_to/cases/case/analysis',
        'priority': 'normal',
        }

    # Check returns from def
    for key, value in config_test_data.items():
        assert config_data[key] == value


def test_parse_sampleinfo_light(files_raw):
    """
    Args:
    files_raw (dict): With dicts from files
    """

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw['sampleinfo']

    # WHEN parsing the MIP output sampleinfo
    sampleinfo_data = files.parse_sampleinfo_light(sampleinfo_raw)

    # THEN it should work
    assert isinstance(sampleinfo_data, dict)

    # THEN it should mark the run as "finished"
    assert sampleinfo_data['is_finished'] is True

    # THEN date should be set
    assert sampleinfo_data['date'] == dateutil.parser.parse('2019-07-05T10:12:03')

    # THEN version should be set
    assert sampleinfo_data['version'] == 'v7.1.0'

def test_get_rank_model_version(files_raw):
    """Test getting the rank model from sample_info file"""

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw['sampleinfo']

    # WHEN getting the rank_model
    rank_model_version = files.get_rank_model_version(sample_info=sampleinfo_raw, rank_model_type='rank_model', step='genmod')

    # THEN the rank model version should be returned
    assert rank_model_version == RANK_MODEL_VERSION

def test_get_rank_model_version_with_program(files_raw):
    """Test getting the rank model from sample_info file with program key"""

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = copy.copy(files_raw['sampleinfo'])

    # Using old MIP style with program instead of recipe
    sampleinfo_raw['program'] = sampleinfo_raw.pop('recipe')

    # WHEN getting the rank_model
    rank_model_version = files.get_rank_model_version(sample_info=sampleinfo_raw, rank_model_type='rank_model', step='genmod')

    # THEN the rank model version should be returned
    assert rank_model_version == RANK_MODEL_VERSION

def test_parse_sampleinfo(files_raw):
    """
    Args:
    files_raw (dict): With dicts from files
    """

    # GIVEN sampleinfo input from a finished analysis
    sampleinfo_raw = files_raw['sampleinfo']

    # WHEN parsing the MIP output sampleinfo
    sampleinfo_data = files.parse_sampleinfo(sampleinfo_raw)

    # THEN it should work
    assert isinstance(sampleinfo_data, dict)

    # THEN it should mark the run as "finished"
    assert sampleinfo_data['is_finished'] is True

    # More in-depth testing
    # Family data
    # Build dict for family return data
    sampleinfo_test_data = {
        'case': 'case',
        'genome_build': 'grch37',
        'version': 'v7.1.0',
        }

    # Check returns from def 1
    for key, value in sampleinfo_test_data.items():
        assert sampleinfo_data[key] == value

    # Sample data
    # Build dict for sample return data
    sampleinfo_test_sample_data = {
        'id': 'mother',
        }

    # Check returns from def 2
    for key, value in sampleinfo_test_sample_data.items():
        for sample_data in sampleinfo_data['samples']:

            if sample_data['id'] != sampleinfo_test_sample_data['id']:
                continue

            assert sample_data[key] == value

    assert len(sampleinfo_raw['analysis_type']) == len(sampleinfo_data['samples'])

def test_get_plink_samples(files_raw):
    """ Test get plink sexcheck from qc_metrics"""

    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw['qcmetrics']

    # WHEN parsing plink output in qc_metrics
    plink_samples = files.get_plink_samples(metrics=qcmetrics_raw)

    expected_plink_samples = {'child': 'male',
                              'father': 'male',
                              'mother': 'female',
                              }
    # THEN the family memebers and their gender should be returned
    assert plink_samples == expected_plink_samples

def test_get_plink_samples_when_program(files_raw):
    """ Test get plink sexcheck from qc_metrics using program key"""

    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = copy.copy(files_raw['qcmetrics'])

    # Using old MIP style with program instead of recipe
    qcmetrics_raw['program'] = qcmetrics_raw.pop('recipe')

    # WHEN parsing plink output in qc_metrics
    plink_samples = files.get_plink_samples(metrics=qcmetrics_raw)

    expected_plink_samples = {'child': 'male',
                              'father': 'male',
                              'mother': 'female',
                              }
    # THEN the family memebers and their gender should be returned
    assert plink_samples == expected_plink_samples

def test_parse_qcmetrics(files_raw):
    """
    Args:
    files_raw (dict): With dicts from files
    """

    # GIVEN qc metrics input from an analysis
    qcmetrics_raw = files_raw['qcmetrics']

    # WHEN parsing it
    qcmetrics_data = files.parse_qcmetrics(qcmetrics_raw)

    # THEN it should work ;-)
    assert isinstance(qcmetrics_data, dict)

    # Sample data
    # Build dict for sample return data
    qcmetrics_test_sample_data = {
        'at_dropout': '1.716704',
        'duplicates': 0.0379523291229131,
        'id': 'mother',
        'insert_size_standard_deviation': 94.353778,
        'gc_dropout': '0.214813',
        'mapped': 0.9974176575073073,
        'median_insert_size': '409',
        'plink_sex': 'female',
        'predicted_sex': 'female',
        'reads': 600006004,
        'strand_balance': 0.50162,
        'target_coverage': 28.643247,
        }

    # Check returns from def
    for key, value in qcmetrics_test_sample_data.items():
        for sample_data in qcmetrics_data['samples']:

            if sample_data['id'] != qcmetrics_test_sample_data['id']:
                continue

            assert sample_data[key] == value

    # Sample coverage data
    # Build dict for sample coverage return data
    qcmetrics_test_sample_cov_data = {
        10: '0.98974',
        20: '0.935455',
        50: '0.002685',
        100: '0.000101',
        }

    # Check returns from def
    for key, value in qcmetrics_test_sample_cov_data.items():
        for sample_data in qcmetrics_data['samples']:

            if sample_data['id'] != qcmetrics_test_sample_data['id']:
                continue

            assert sample_data['completeness_target'][key] == value
