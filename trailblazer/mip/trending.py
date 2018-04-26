# -*- coding: utf-8 -*-
""" Get MIP data for trending."""

from trailblazer.mip import files


def parse_mip_analysis(mip_config_raw: dict, qcmetrics_raw: dict, sampleinfo_raw: dict) -> dict:
    """Parse the output analysis files from MIP for adding info
    to trend database

    Args:
        mip_config_raw (dict): raw YAML input from MIP analysis config file
        qcmetrics_raw (dict): raw YAML input from MIP analysis qc metric file
        sampleinfo_raw (dict): raw YAML input from MIP analysis qc sample info file
    Returns:
        dict: parsed data
    """

    outdata = _define_output_dict()

    _config(mip_config_raw, outdata)
    _qc_metrics(outdata, qcmetrics_raw)
    _qc_sample_info(outdata, sampleinfo_raw)

    return outdata


def _qc_sample_info(outdata, sampleinfo_raw):
    sampleinfo_data = _parse_qc_sample_info_file(sampleinfo_raw)
    _add_mip_version(outdata, sampleinfo_data)
    _add_genome_build(outdata, sampleinfo_data)


def _qc_metrics(outdata, qcmetrics_raw):
    qcmetrics_data = _parse_qc_metric_file_into_dict(qcmetrics_raw)
    _add_sample_level_info_from_qc_metric_file(outdata, qcmetrics_data)


def _config(mip_config_raw, outdata):
    config_data = _parse_raw_mip_config_into_dict(mip_config_raw)
    _add_family_id(config_data, outdata)
    _add_all_samples_from_mip_config(config_data, outdata)


def _add_genome_build(outdata, sampleinfo_data):
    outdata['genome_build'] = sampleinfo_data['genome_build']


def _add_mip_version(outdata, sampleinfo_data):
    outdata['mip_version'] = sampleinfo_data['version']


def _parse_qc_sample_info_file(sampleinfo_raw):
    sampleinfo_data = files.parse_sampleinfo(sampleinfo_raw)
    return sampleinfo_data


def _add_sample_level_info_from_qc_metric_file(outdata, qcmetrics_data):
    for sample_data in qcmetrics_data['samples']:
        _add_duplicate_reads(outdata, sample_data)
        _add_mapped_reads(outdata, sample_data)
        _add_predicted_sex(outdata, sample_data)


def _add_predicted_sex(outdata, sample_data):
    outdata['analysis_sex'][sample_data['id']] = sample_data['predicted_sex']


def _add_mapped_reads(outdata, sample_data):
    mapped_reads_percent = sample_data['mapped'] * 100
    outdata['mapped_reads'][sample_data['id']] = mapped_reads_percent


def _add_duplicate_reads(outdata, sample_data):
    duplicates_percent = sample_data['duplicates'] * 100
    outdata['duplicates'][sample_data['id']] = duplicates_percent


def _parse_qc_metric_file_into_dict(qcmetrics_raw):
    qcmetrics_data = files.parse_qcmetrics(qcmetrics_raw)
    return qcmetrics_data


def _parse_raw_mip_config_into_dict(mip_config_raw):
    config_data = files.parse_config(mip_config_raw)
    return config_data


def _define_output_dict():
    outdata = {
        'analysis_sex': {},
        'family': None,
        'duplicates': {},
        'genome_build': None,
        'mapped_reads': {},
        'mip_version': None,
        'sample_ids': [],
    }
    return outdata


def _add_all_samples_from_mip_config(config_data, outdata):
    for sample_data in config_data['samples']:
        outdata['sample_ids'].append(sample_data['id'])


def _add_family_id(config_data, outdata):
    outdata['family'] = config_data['family']
