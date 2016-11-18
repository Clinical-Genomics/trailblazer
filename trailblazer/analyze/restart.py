# -*- coding: utf-8 -*-
import yaml

ALIGN = ['pGZipFastq', 'pFastQC', 'pBwaMem', 'pPicardToolsMergeSamFiles',
         'pPicardToolsMarkduplicates', 'pGATKRealigner',
         'pGATKBaseRecalibration']
COVERAGE = ['pChanjoSexCheck', 'pSambambaDepth',
            'pPicardToolsCollectMultipleMetrics',
            'pPicardToolsCalculateHSMetrics']
SV = ['pManta', 'pSVCombineVariantCallSets', 'pSVVariantEffectPredictor',
      'pSVVCFParser', 'pSVRankVariants']
SNV = ['pSamToolsMpileUp', 'pFreebayes', 'pGATKHaploTypeCaller',
       'pGATKGenoTypeGVCFs', 'pGATKVariantRecalibration',
       'pGATKCombineVariantCallSets', 'pPrepareForVariantAnnotationBlock',
       'pVT', 'pGATKVariantEvalAll', 'pGATKVariantEvalExome',
       'pVariantEffectPredictor', 'pSnpEff', 'pVCFParser', 'pRankVariants']
STATS = ['pSampleCheck', 'pQCCollect', 'pMultiQC', 'pRemoveRedundantFiles',
         'pAnalysisRunStatus', 'pSacct']
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
                             start_step='pGATKVariantRecalibration',
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
