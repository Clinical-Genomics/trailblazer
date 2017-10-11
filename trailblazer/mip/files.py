# -*- coding: utf-8 -*-
"""Parse the MIP config file."""


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
    return {
        'date': data['analysis_date'],
        'is_finished': True if data['analysisrunstatus'] == 'finished' else False,
        'genome_build': genome_build_str,
        'version': data['mip_version'],
        'pedigree_path': data['pedigree_minimal'],
        'samples': [{
            'id': sample_id,
            'bam': sample_data['most_complete_bam']['path'],
            'sambamba': list(sample_data['program']['sambamba_depth'].values())[0]['bed']['path'],
        } for sample_id, sample_data in data['sample'].items()],
        'qcmetrics_path': data['program']['qccollect']['qccollect_metrics_file']['path'],
        'sv': {
            'clinical_vcf': (data['sv_vcf_binary_file']['clinical']['path'] if
                             'sv_vcf_binary_file' in data else None),
            'research_vcf': (data['sv_vcf_binary_file']['research']['path'] if
                             'sv_vcf_binary_file' in data else None),
            'bcf': data.get('sv_bcf_file'),
        },
        'snv': {
            'bcf': data['bcf_file']['path'],
            'gbcf': data['gbcf_file']['path'],
            'clinical_vcf': data['vcf_binary_file']['clinical']['path'],
            'research_vcf': data['vcf_binary_file']['research']['path'],
        },
    }


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
    for sample_id, sample_metrics in metrics['sample'].items():
        main_key = [key for key in sample_metrics.keys() if '_lanes_' in key][0]
        sample_data = {
            'id': sample_id,
            'predicted_sex': sample_metrics[main_key]['chanjo_sexcheck']['gender'],
            'duplicates': sample_metrics[main_key]['markduplicates']['fraction_duplicates'],
        }
        data['samples'].append(sample_data)
    return data
