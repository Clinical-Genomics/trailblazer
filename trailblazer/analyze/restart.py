# -*- coding: utf-8 -*-
from path import path
import yaml

from .start import start_mip


def restart_mip(script_dir, config_path, **start_kwargs):
    """Restart a MIP run."""
    with open(config_path, 'r') as stream:
        values = yaml.load(stream)
    script_content = start_mip(analysis_config=config_path, **start_kwargs)
    customer = values['instanceTag'][0]
    family = values['familyID']
    out_filename = "{}-{}.sh".format(customer, family)
    out_path = path(script_dir).joinpath(out_filename)
    with out_path.open('wb') as out_stream:
        out_stream.write(script_content)


def update_maxgaussian(config_path):
    """Update MIP config to prepare for restart after max gaussian error."""
    with open(config_path, 'r') as stream:
        values = yaml.load(stream)

    # update the requried values
    # set Max Gaussian flag for SNVs
    values['GATKVariantReCalibrationSnvMaxGaussians'] = 1
    # update early (successful) programs to dry run
    early_programs = ['pBwaMem', 'pChanjoSexCheck', 'pFastQC', 'pFreebayes',
                      'pGATKBaseRecalibration', 'pGATKGenoTypeGVCFs',
                      'pGATKHaploTypeCaller', 'pGATKRealigner', 'pGZipFastq',
                      'pManta', 'pPicardToolsCalculateHSMetrics',
                      'pPicardToolsCollectMultipleMetrics',
                      'pPicardToolsMarkduplicates',
                      'pPicardToolsMergeSamFiles',
                      'pSamToolsMpileUp', 'pSambambaDepth']
    for program_key in early_programs:
        #assert values[program_key] in (1, '1')
        values[program_key] = 2

    with open(config_path, 'w') as out_stream:
        yaml_out = yaml.dump(values, default_flow_style=False)
        yaml_out_correct = yaml_out.replace('\n- ', '\n    - ')
        out_stream.write(yaml_out_correct)
