# -*- coding: utf-8 -*-
"""Test MIP files"""

import dateutil

from trailblazer.mip import files


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
        'multiqc_html': '/path_to/case/case/multiqc_ar/multiqc_report.html',
        'multiqc_json': '/path_to/case/case/multiqc_ar/multiqc_data/multiqc_data.json',
        'pedigree': '/path_to/cases/case/case_pedigree.yaml',
        'pedigree_path': '/path_to/case/case.fam',
        'qcmetrics_path': '/path_to/case/case_qc_metrics.yaml',
        'sv_combinevariantcallsets_path':
            '/path_to/case/case/sv_combinevariantcallsets/case_comb.vcf',
        'version': 'v7.1.0',
        'version_collect': '/path_to/case/case/version_collect_ar/case_vcol.yaml',
        }

    # Check returns from def 1
    for key, value in sampleinfo_test_data.items():
        assert sampleinfo_data[key] == value

    # Sample data
    # Build dict for sample return data
    sampleinfo_test_sample_data = {
        'cram': '/path_to/case/mother/gatk_baserecalibration/mother_lanes_1_sorted_md_brecal.cram',
        'chanjo_sexcheck': (
            '/path_to/case/mother/chanjo_sexcheck/mother_lanes_1_sorted_md_brecal_sex.tsv'),
        'id': 'mother',
        'chromograph': '/path_to/case/mother/chromograph_ar/mother_lanes_1234_sorted_md_brecal_tcov_chromograph.tar.gz',
        'sambamba': ('/path_to/case/mother/sambamba_depth'
                     '/mother_lanes_1_sorted_md_brecal_coverage.bed'),
        'sex': 'female',
        'subsample_mt': ('/path_to/case/mother/samtools_subsample_mt'
                         '/mother_lanes_1_sorted_md_brecal_subsample_MT.bam'),
        'vcf2cytosure': '/path_to/case/case/vcf2cytosure_ar/case_cyto.mother.cgh',
        }

    # Check returns from def 2
    for key, value in sampleinfo_test_sample_data.items():
        for sample_data in sampleinfo_data['samples']:

            if sample_data['id'] != sampleinfo_test_sample_data['id']:
                continue

            assert sample_data[key] == value

    assert len(sampleinfo_raw['analysis_type']) == len(sampleinfo_data['samples'])

    # Snv data
    # Build dict for snv return data
    sampleinfo_test_snv_data = {
        'clinical_vcf': ('/path_to/case/case/endvariantannotationblock'
                         '/case_gatkcomb_rhocall_vt_frqf_cadd_vep_parsed_snpeff_ranked.selected'
                         '.vcf.gz'),
        'research_vcf': ('/path_to/case/case/endvariantannotationblock'
                         '/case_gatkcomb_rhocall_vt_frqf_cadd_vep_parsed_snpeff_ranked.vcf.gz'),
        'bcf': '/path_to/case/case/gatk_combinevariantcallsets/case_gatkcomb.bcf',
        }

    # Check returns from def 3
    for key, value in sampleinfo_test_snv_data.items():
        assert sampleinfo_data['snv'][key] == value

    # SV data
    # Build dict for sv return data
    sampleinfo_test_sv_data = {
        'clinical_vcf': ('/path_to/case/case/sv_reformat/case_comb_ann_vep_parsed_ranked.selected'
                         '.vcf.gz'),
        'research_vcf': '/path_to/case/case/sv_reformat/case_comb_ann_vep_parsed_ranked.vcf.gz',
        'bcf': '/path_to/case/case/sv_combinevariantcallsets/case_comb.bcf',
        'merged': '/path_to/case/case/sv_combinevariantcallsets/case_comb.vcf',
        }

    # Check returns from def 4
    for key, value in sampleinfo_test_sv_data.items():
        assert sampleinfo_data['sv'][key] == value

    # Peddy data
    # Build dict for peddy return data
    sampleinfo_test_peddy_data = {
        'ped_check': '/path_to/case/case/peddy_ar/case_gatkcomb.ped_check.csv',
        'ped': '/path_to/case/case/peddy_ar/case_gatkcomb.peddy.ped',
        'sex_check': '/path_to/case/case/peddy_ar/case_gatkcomb.sex_check.csv',
        }

    # Check returns from def 5
    for key, value in sampleinfo_test_peddy_data.items():
        assert sampleinfo_data['peddy'][key] == value


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
