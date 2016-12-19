# -*- coding: utf-8 -*-
import yaml

ALIGN = ['pgzip_fastq', 'pfastqc', 'pbwa_mem', 'ppicardtools_mergesamfiles',
         'ppicardtools_markduplicates', 'pgatk_realigner',
         'pgatk_baserecalibration']
COVERAGE = ['pchanjo_sexcheck', 'psambamba_depth',
            'ppicardtools_collectmultiplemetrics',
            'ppicardtools_calculatehsmetrics']
SV = ['pmanta', 'psv_combinevariantcallsets', 'psv_varianteffectpredictor',
      'psv_vcfparser', 'psv_rankvariant']
SNV = ['psamtools_mpileup', 'pfreebayes', 'pgatk_haplotypecaller',
       'pgatk_genotypegvcfs', 'pgatk_variantrecalibration',
       'pgatk_combinevariantcallsets', 'pprepareforvariantannotationblock',
       'pvt', 'pgatk_variantevalall', 'pgatk_variantevalexome',
       'pvarianteffectpredictor', 'psnpeff', 'pvcfparser', 'prankvariant']
STATS = ['psamplecheck', 'pqccollect', 'pmultiqc', 'premoveredundantfiles',
         'panalysisrunstatus', 'psacct']
PROGRAMS = ALIGN + COVERAGE + SV + SNV + STATS

BRANCHES = {'align': ALIGN, 'coverage': COVERAGE, 'sv': SV, 'snv': SNV,
            'stats': STATS}


def update_config(config_path, start_step=None, disable_branches=None,
                  **extras):
    """Generalize modifying config values for restart."""
    with open(config_path, 'r') as in_handle:
        config_values = yaml.load(in_handle)

    start_step = start_step or PROGRAMS[0]
    start_from(config_values, start_step)

    for branch in (disable_branches or []):
        disable_branch(config_values, branch)

    for key, value in extras.items():
        config_values[key] = value

    return config_values


def write_config(config_path, config_values):
    """Update MIP config file."""
    with open(config_path, 'w') as out_stream:
        yaml_out = yaml.dump(config_values, default_flow_style=False)
        yaml_out_correct = yaml_out.replace('\n- ', '\n    - ')
        out_stream.write(yaml_out_correct)


def update_maxgaussian(config_path):
    """Update MIP config to prepare for restart after max gaussian error."""
    new_conf = update_config(config_path,
                             start_step='pgatk_variantrecalibration',
                             GATKVariantReCalibrationSnvMaxGaussians=1)
    return new_conf


def disable_branch(config_values, branch):
    """Disable a branch of jobs."""
    if branch not in BRANCHES:
        raise ValueError("invalid branch choice: {}".format(branch))
    for step_key in BRANCHES[branch]:
        config_values[step_key] = 0


def start_from(config_values, step):
    """Restart and analysis from a particular step."""
    start_index = PROGRAMS.index(step)
    # set upstream steps to run in dry run mode
    for step_key in PROGRAMS[:start_index]:
        config_values[step_key] = 2

    # enable downstream steps
    for step_key in PROGRAMS[start_index:]:
        config_values[step_key] = 1
