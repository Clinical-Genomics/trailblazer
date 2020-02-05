# -*- coding: utf-8 -*-
"""Parse the MIP config file."""
from typing import TextIO
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
        'case': data['case_id'],
        'samples': [{
            'id': sample_id,
            'type': analysis_type,
        } for sample_id, analysis_type in data['analysis_type'].items()],
        'config_path': data['config_file_analysis'],
        'is_dryrun': True if 'dry_run_all' in data else False,
        'log_path': data['log_file'],
        'out_dir': data['outdata_dir'],
        'priority': data['slurm_quality_of_service'],
        'sampleinfo_path': data['sample_info_file'],
    }


def parse_sampleinfo_light(data: dict) -> dict:
    """Parse MIP sample info file and retrieve mip_version, date, and status

    Args:
        data (dict): raw YAML input from MIP qc sample info file

    Returns:
        dict: {'version': str, 'date': str, 'is_finished': str}

    """
    outdata = {
        'date': data['analysis_date'],
        'version': data['mip_version'],
        'is_finished': True if data['analysisrunstatus'] == 'finished' else False
    }

    return outdata

def parse_sampleinfo(data: dict) -> dict:
    """Parse MIP sample info file.

    Args:
        data (dict): raw YAML input from MIP qc sample info file

    Returns:
        dict: parsed data
    """
    genome_build = data['human_genome_build']
    genome_build_str = f"{genome_build['source']}{genome_build['version']}"
    if 'sv_combinevariantcallsets' in data['recipe']:
        sv_combinevariantcallsets_path = \
            (f"{data['recipe']['sv_combinevariantcallsets']['path']}")
    else:
        sv_combinevariantcallsets_path = ''
    outdata = {
        'date': data['analysis_date'],
        'case': data['case'],
        'genome_build': genome_build_str,
        'is_finished': True if data['analysisrunstatus'] == 'finished' else False,
        'multiqc_html': data['recipe']['multiqc'][data['case'] + '_html']['path'],
        'multiqc_json': data['recipe']['multiqc'][data['case'] + '_json']['path'],
        'peddy': {
            'ped': (data['recipe']['peddy_ar']['peddy']['path'] if
                    'peddy_ar' in data['recipe'] else None),
            'ped_check': (data['recipe']['peddy_ar']['ped_check']['path'] if
                          'peddy_ar' in data['recipe'] else None),
            'sex_check': (data['recipe']['peddy_ar']['sex_check']['path'] if
                          'peddy_ar' in data['recipe'] else None),
        },
        'pedigree': data['pedigree_file']['path'],
        'pedigree_path': data['pedigree_minimal'],
        'qcmetrics_path': data['recipe']['qccollect_ar']['path'],
        'rank_model_version': data['recipe']['genmod']['rank_model']['version'],
        'samples': [],
        'snv': {
            'bcf': data['most_complete_bcf']['path'],
            'clinical_vcf': data['vcf_binary_file']['clinical']['path'],
            'research_vcf': data['vcf_binary_file']['research']['path'],
        },
        'str_vcf': data['recipe'].get('expansionhunter', {}).get('path'),
        'sv': {
            'bcf': data['recipe']['sv_combinevariantcallsets'].get('sv_bcf_file', {}).get('path'),
            'clinical_vcf': (data['sv_vcf_binary_file']['clinical']['path'] if
                             'sv_vcf_binary_file' in data else None),
            'merged': sv_combinevariantcallsets_path,
            'research_vcf': (data['sv_vcf_binary_file']['research']['path'] if
                             'sv_vcf_binary_file' in data else None),
        },
        'sv_rank_model_version': data['recipe']['sv_genmod']['sv_rank_model']['version'],
        'sv_combinevariantcallsets_path': sv_combinevariantcallsets_path,
        'version': data['mip_version'],
        'version_collect': data['recipe']['version_collect_ar']['path'],
    }

    for sample_id, sample_data in data['sample'].items():
        sample = {
            'id': sample_id,
            'cram': sample_data['most_complete_bam']['path'],
            # chromograph is only for wgs and trio data
            'chromograph': (sample_data['recipe']['chromograph_ar']['path']  if 'chromograph_ar' in sample_data['recipe']
                             else None),
            'sambamba': list(sample_data['recipe']['sambamba_depth'].values())[0]['path'],
            'sex': sample_data['sex'],
            # subsample mt is only for wgs data
            'subsample_mt': (list(sample_data['recipe']['samtools_subsample_mt'].values())
                             [0]['path'] if 'samtools_subsample_mt' in sample_data['recipe']
                             else None),
            'vcf2cytosure': list(sample_data['recipe']['vcf2cytosure'].values())[0]['path'],
        }
        chanjo_sexcheck = list(sample_data['recipe']['chanjo_sexcheck'].values())[0]
        sample['chanjo_sexcheck'] = chanjo_sexcheck['path']
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
        'samples': [],
    }

    plink_samples = {}
    plink_sexcheck = metrics['recipe'].get('plink_sexcheck', {}).get('sample_sexcheck')
    if isinstance(plink_sexcheck, str):
        sample_id, sex_number = plink_sexcheck.strip().split(':', 1)
        plink_samples[sample_id] = PED_SEX_MAP.get(int(sex_number))
    elif isinstance(plink_sexcheck, list):
        for sample_raw in plink_sexcheck:
            sample_id, sex_number = sample_raw.split(':', 1)
            plink_samples[sample_id] = PED_SEX_MAP.get(int(sex_number))

    for sample_id, sample_metrics in metrics['sample'].items():

        # Bam stats metrics
        bam_stats = [values['bamstats'] for key, values in sample_metrics.items()
                     if key[:-8].endswith('_lane')]
        total_reads = sum(int(bam_stat['raw_total_sequences']) for bam_stat in bam_stats)
        total_mapped = sum(int(bam_stat['reads_mapped']) for bam_stat in bam_stats)

        # Picard metrics
        metrics_keys = [key for key in sample_metrics.keys() if '_lanes_' in key]
        main_key = metrics_keys[0]
        hsmetrics_key = metrics_keys[1]
        multimetrics_key = metrics_keys[2]
        sex_check_key = metrics_keys[3]

        hs_metrics = sample_metrics[hsmetrics_key]['collecthsmetrics']['header']['data']
        multiple_inst_metrics = \
            sample_metrics[multimetrics_key]['collectmultiplemetricsinsertsize']['header']['data']
        multiple_metrics = \
            sample_metrics[multimetrics_key]['collectmultiplemetrics']['header']['pair']

        sample_data = {
            'at_dropout': hs_metrics['AT_DROPOUT'],
            'completeness_target': {
                10: hs_metrics['PCT_TARGET_BASES_10X'],
                20: hs_metrics['PCT_TARGET_BASES_20X'],
                50: hs_metrics['PCT_TARGET_BASES_50X'],
                100: hs_metrics['PCT_TARGET_BASES_100X'],
            },
            'duplicates': float(sample_metrics[main_key]['markduplicates']['fraction_duplicates']),
            'gc_dropout': hs_metrics['GC_DROPOUT'],
            'id': sample_id,
            'median_insert_size':  multiple_inst_metrics['MEDIAN_INSERT_SIZE'],
            'mapped': total_mapped / total_reads,
            'plink_sex': plink_samples.get(sample_id),
            'predicted_sex': sample_metrics[sex_check_key]['chanjo_sexcheck']['gender'],
            'reads': total_reads,
            'insert_size_standard_deviation': float(multiple_inst_metrics['STANDARD_DEVIATION']),
            'strand_balance': float(multiple_metrics['STRAND_BALANCE']),
            'target_coverage': float(hs_metrics['MEAN_TARGET_COVERAGE']),
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
