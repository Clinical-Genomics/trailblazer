"""Parse the MIP config, qc_metric and qc_sampleinfo file."""


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
        'case': data['case_id'] if 'case_id' in data else data['family_id'],  # family_id for MIP<7
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


def get_sampleinfo_date(data: dict) -> str:
    """Get MIP sample info date.

    Args:
        data (dict): raw YAML input from MIP qc sample info file

    Returns:
        str: analysis date
    """

    return data['analysis_date']

def get_rank_model_version(sample_info: dict, rank_model_type: str, step: str) -> str:
    """Get rank model version"""
    rank_model_version = None
    for key in ('recipe', 'program'):
        if key in sample_info:
            rank_model_version = sample_info[key][step][rank_model_type]['version']
            break
    return rank_model_version

def parse_sampleinfo(data: dict) -> dict:
    """Parse MIP sample info file.

    Args:
        data (dict): raw YAML input from MIP qc sample info file

    Returns:
        dict: parsed data
    """
    genome_build = data['human_genome_build']
    genome_build_str = f"{genome_build['source']}{genome_build['version']}"
    outdata = {
        'date': data['analysis_date'],
        'genome_build': genome_build_str,
        'case': data['case'],
        'is_finished': True if data['analysisrunstatus'] == 'finished' else False,
        'rank_model_version': get_rank_model_version(sample_info=data, rank_model_type='rank_model', step='genmod'),
        'samples': [],
        'sv_rank_model_version': get_rank_model_version(sample_info=data, rank_model_type='sv_rank_model', step='sv_genmod'),
        'version': data['mip_version'],
    }

    for sample_id in data['sample'].items():
        sample = {
            'id': sample_id,
        }
        outdata['samples'].append(sample)

    return outdata

def get_plink_samples(metrics: dict) -> dict:
    """Get plink samples"""
    plink_sexcheck = None
    plink_samples = {}
    if 'recipe' in metrics:
        plink_sexcheck = metrics['recipe'].get('plink_sexcheck', {}).get('sample_sexcheck')
    elif 'program' in metrics:    # for MIP<7
        plink_sexcheck = metrics['program'].get('plink_sexcheck', {}).get('sample_sexcheck')
    if isinstance(plink_sexcheck, str):
        sample_id, sex_number = plink_sexcheck.strip().split(':', 1)
        plink_samples[sample_id] = PED_SEX_MAP.get(int(sex_number))
    elif isinstance(plink_sexcheck, list):
        for sample_raw in plink_sexcheck:
            sample_id, sex_number = sample_raw.split(':', 1)
            plink_samples[sample_id] = PED_SEX_MAP.get(int(sex_number))
    return plink_samples

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

    plink_samples = get_plink_samples(metrics=metrics)

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
