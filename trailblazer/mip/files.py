# -*- coding: utf-8 -*-
"""Parse the MIP config file."""
from typing import List, TextIO
import csv

PED_SEX_MAP = {1: 'male', 2: 'female', 0: 'unknown'}


def parse_config(data: dict) -> dict:
    """Parse MIP config file.

    Args:
        data (dict): raw YAML input from MIP analysis config file

    Returns:
        dict: parsed data
    """
    return {
        'email': data.get('email'),
        'family': data['family_id'],
        'samples': [{
            'id': sample_id,
            'type': analysis_type,
        } for sample_id, analysis_type in data['analysis_type'].items()],
        'is_dryrun': True if data['dry_run_all'] == '2' else False,
        'log_path': data['log_file'],
        'sampleinfo_path': data['sample_info_file'],
        'priority': data['slurm_quality_of_service'],
        'out_dir': data['outdata_dir'],
        'config_path': data['config_file_analysis'],
    }


def parse_sampleinfo(data: dict) -> dict:
    """Parse MIP sample info file.

    Args:
        data (dict): raw YAML input from MIP qc sample info file

    Returns:
        dict: parsed data
    """
    genome_build = data['human_genome_build']
    genome_build_str = f"{genome_build['source']}{genome_build['version']}"
    if 'svdb' in data['program']:
        svdb_outpath = (f"{data['program']['svdb']['outdirectory']}/"
                        f"{data['program']['svdb']['outfile']}")
    else:
        svdb_outpath = ''
    outdata = {
        'date': data['analysis_date'],
        'is_finished': True if data['analysisrunstatus'] == 'finished' else False,
        'genome_build': genome_build_str,
        'version': data['mip_version'],
        'pedigree_path': data['pedigree_minimal'],
        'samples': [],
        'qcmetrics_path': data['program']['qccollect']['qccollect_metrics_file']['path'],
        'sv': {
            'clinical_vcf': (data['sv_vcf_binary_file']['clinical']['path'] if
                             'sv_vcf_binary_file' in data else None),
            'research_vcf': (data['sv_vcf_binary_file']['research']['path'] if
                             'sv_vcf_binary_file' in data else None),
            'bcf': data.get('sv_bcf_file', {}).get('path'),
            'merged': svdb_outpath,
        },
        'snv': {
            'bcf': data['bcf_file']['path'],
            'gbcf': data['gbcf_file']['path'],
            'clinical_vcf': data['vcf_binary_file']['clinical']['path'],
            'research_vcf': data['vcf_binary_file']['research']['path'],
        },
        'peddy': {
            'ped_check': (data['program']['peddy']['ped_check']['path'] if
                          'peddy' in data['program'] else None),
            'ped': (data['program']['peddy']['peddy']['path'] if
                    'peddy' in data['program'] else None),
            'sex_check': (data['program']['peddy']['sex_check']['path'] if
                          'peddy' in data['program'] else None),
        },
        'family': data['family'],
    }

    for sample_id, sample_data in data['sample'].items():
        sample = {
            'id': sample_id,
            'bam': sample_data['most_complete_bam']['path'],
            'sambamba': list(sample_data['program']['sambamba_depth'].values())[0]['bed']['path'],
            'sex': sample_data['sex'],
        }
        chanjo_sexcheck = list(sample_data['program']['chanjo_sexcheck'].values())[0]
        sexcheck_path = f"{chanjo_sexcheck['outdirectory']}/{chanjo_sexcheck['outfile']}"
        sample['chanjo_sexcheck'] = sexcheck_path
        outdata['samples'].append(sample)

    return outdata


def parse_qcmetrics(metrics: dict) -> dict:
    """Parse MIP qc metrics file.

    Args:
        metrics (dict): raw YAML input from MIP qc metrics file

    Returns:
        dict: parsed data
    """
    data = {
        'versions': {
            'freebayes': metrics['program']['freebayes']['version'],
            'gatk': metrics['program']['gatk']['version'],
            'manta': metrics['program'].get('manta', {}).get('version'),
            'samtools': metrics['program']['samtools']['version'],
            'vep': metrics['program']['varianteffectpredictor']['version'],
        },
        'samples': [],
    }

    plink_samples = {}
    plink_sexcheck = metrics['program'].get('plink_sexcheck', {}).get('sample_sexcheck')
    if isinstance(plink_sexcheck, str):
        sample_id, sex_number = plink_sexcheck.strip().split(':', 1)
        plink_samples[sample_id] = PED_SEX_MAP.get(int(sex_number))
    elif isinstance(plink_sexcheck, list):
        for sample_raw in plink_sexcheck:
            sample_id, sex_number = sample_raw.split(':', 1)
            plink_samples[sample_id] = PED_SEX_MAP.get(int(sex_number))

    for sample_id, sample_metrics in metrics['sample'].items():
        bam_stats = [values['bamstats'] for key, values in sample_metrics.items()
                     if key[:-1].endswith('.lane')]
        total_reads = sum(int(bam_stat['raw_total_sequences']) for bam_stat in bam_stats)
        total_mapped = sum(int(bam_stat['reads_mapped']) for bam_stat in bam_stats)

        main_key = [key for key in sample_metrics.keys() if '_lanes_' in key][0]

        hs_metrics = sample_metrics[main_key]['collecthsmetrics']['header']['data']
        multiple_metrics = sample_metrics[main_key]['collectmultiplemetrics']['header']['pair']
        sample_data = {
            'id': sample_id,
            'predicted_sex': sample_metrics[main_key]['chanjo_sexcheck']['gender'],
            'duplicates': float(sample_metrics[main_key]['markduplicates']['fraction_duplicates']),
            'plink_sex': plink_samples.get(sample_id),
            'reads': total_reads,
            'mapped': total_mapped / total_reads,
            'target_coverage': float(hs_metrics['MEAN_TARGET_COVERAGE']),
            'strand_balance': float(multiple_metrics['STRAND_BALANCE']),
            'completeness_target': {
                10: hs_metrics['PCT_TARGET_BASES_10X'],
                20: hs_metrics['PCT_TARGET_BASES_20X'],
                50: hs_metrics['PCT_TARGET_BASES_50X'],
                100: hs_metrics['PCT_TARGET_BASES_100X'],
            },
        }
        data['samples'].append(sample_data)
    return data


def parse_peddy_sexcheck(handle: TextIO):
    """Parse Peddy sexcheck output."""
    data = {}
    samples = csv.DictReader(handle)
    for sample in samples:
        data[sample['sample_id']] = {
            'predicted_sex': sample['predicted_sex'],
            'het_ratio': float(sample['het_ratio']),
            'error': True if sample['error'] == 'True' else False,
        }
    return data


def parse_chanjo_sexcheck(handle: TextIO):
    """Parse Chanjo sex-check output."""
    samples = csv.DictReader(handle, delimiter='\t')
    for sample in samples:
        return {
            'predicted_sex': sample['sex'],
            'x_coverage': float(sample['#X_coverage']),
            'y_coverage': float(sample['Y_coverage']),
        }
