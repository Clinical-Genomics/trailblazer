# -*- coding: utf-8 -*-
"""Test MIP files"""

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

    # THEN it should work and the dry run check should be "no"
    assert config_data['is_dryrun'] is False

    # ... and should include all samples
    assert len(config_raw['analysis_type']) == len(config_data['samples'])

    # Build dict for return data
    config_test_data = {
        'config_path': 'tests/fixtures/family/family_config.yaml',
        'email': 'emilia.ottosson@scilifelab.se',
        'family': 'family',
        'log_path': 'tests/fixtures/family/mip.pl_2017-06-17T12:11:42.log',
        'sampleinfo_path': ('/mnt/hds/proj/bioinfo/MIP_ANALYSIS/' +
                            'customers/cust003/family/analysis/' +
                            'family_qc_sample_info.yaml'),
        'out_dir': ('/mnt/hds/proj/bioinfo/MIP_ANALYSIS/customers/' +
                    'cust003/family/analysis'),
        'priority': 'normal',
        }

    # Check returns from def
    for key, value in config_test_data.items():
        assert config_data[key] == value

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

    ### More in-depth testing
    ## Family data
    # Build dict for family return data
    sampleinfo_test_data = {
        'family': 'family',
        'genome_build': 'GRCh37',
        'pedigree_path': '/path_to/family/family.fam',
        'qcmetrics_path': ('/path_to/family/family_qc_metrics.yaml'),
        'svdb_outpath': 'path/to/118_sorted_md_brecal_comb_SV.vcf',
        'version': 'v6.0.0',
        }

    # Check returns from def
    for key, value in sampleinfo_test_data.items():
        assert sampleinfo_data[key] == value

    ## Sample data
    # Build dict for sample return data
    sampleinfo_test_sample_data = {
        'id': 'sample',
        'bam': '/path_to/sample/bwa/sample_lanes_7777_sorted_md_brecal.bam',
        'sambamba': ('/path_to/sample/bwa/coveragereport/sample_lanes_7777' +
                     '_sorted_md_brecal_coverage.bed'),
        'sex': 'female',
        'chanjo_sexcheck': ('/path_to/sample/bwa/coveragereport/' +
                            'sample_lanes_7777_sorted_md_brecal.sexcheck'),
        }

    # Check returns from def
    for key, value in sampleinfo_test_sample_data.items():
        for sample_data in sampleinfo_data['samples']:
            assert sample_data[key] == value

    assert len(sampleinfo_raw['analysis_type']) == len(sampleinfo_data['samples'])

    ## Snv data
    # Build dict for snv return data
    sampleinfo_test_snv_data = {
        'clinical_vcf': ('/path_to/family_sorted_md_brecal_gvcf_vrecal_comb' +
                         '_vt_vep_parsed_snpeff_ranked_BOTH.selected.vcf.gz'),
        'research_vcf': ('/path_to/family_sorted_md_brecal_gvcf_vrecal_comb' +
                         '_vt_vep_parsed_snpeff_ranked_BOTH.vcf.gz'),
        'bcf': '/path_to/family_sorted_md_brecal_gvcf_vrecal_comb_BOTH.bcf',
        'gbcf': '/path_to/gatk/family_sorted_md_brecal_gvcf_BOTH.bcf'
        }

    # Check returns from def
    for key, value in sampleinfo_test_snv_data.items():
        assert sampleinfo_data['snv'][key] == value

    ## SV data
    # Build dict for sv return data
    sampleinfo_test_sv_data = {
        'clinical_vcf': ('/path_to/family_sorted_md_brecal_comb_vep_' +
                         'parsed_ranked_SV.selected.vcf.gz'),
        'research_vcf': ('/path_to/family_sorted_md_brecal_comb_vep_' +
                         'parsed_ranked_SV.vcf.gz'),
        'bcf': '/path_to/family_sorted_md_brecal_comb_SV.bcf',
        'merged': 'path/to/118_sorted_md_brecal_comb_SV.vcf',
        }

    # Check returns from def
    for key, value in sampleinfo_test_sv_data.items():
        assert sampleinfo_data['sv'][key] == value

    ## Peddy data
    # Build dict for peddy return data
    sampleinfo_test_peddy_data = {
        'ped_check': '/path_to/118.ped_check.csv',
        'ped': '/path_to/118.peddy.ped',
        'sex_check': '/path_to/118.sex_check.csv',
        }

    # Check returns from def
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

    ## Version data
    # Build dict for version return data
    qcmetrics_test_version_data = {
        'freebayes': 'v1.0.2',
        'gatk': 3.6,
        'manta': '1.0.3',
        'bcftools': '1.3.1+htslib-1.3.1',
        'vep': 'v87',
        }

    # Check returns from def
    for key, value in qcmetrics_test_version_data.items():
        assert qcmetrics_data['versions'][key] == value

    ## Sample data
    # Build dict for sample return data
    qcmetrics_test_sample_data = {
        'at_dropout': 0.126963,
        'duplicates': 0.132719986683768,
        'id': 'sample',
        'insert_size_standard_deviation': 89.871783,
        'gc_dropout': 3.956909,
        'mapped': 0.9850732625744484,
        'median_insert_size': 413,
        'plink_sex': 'female',
        'predicted_sex': 'female',
        'reads': 949878168,
        'strand_balance': 0.499558,
        'target_coverage': 37.428611,
        }

    # Check returns from def
    for key, value in qcmetrics_test_sample_data.items():
        for sample_data in qcmetrics_data['samples']:
            assert sample_data[key] == value

    ## Sample coverage data
    # Build dict for sample coverage return data
    qcmetrics_test_sample_cov_data = {
        10: 0.991187,
        20: 0.984713,
        50: 0.063229,
        100: 0.000372,
        }
    # Check returns from def
    for key, value in qcmetrics_test_sample_cov_data.items():
        for sample_data in qcmetrics_data['samples']:
            assert sample_data['completeness_target'][key] == value
