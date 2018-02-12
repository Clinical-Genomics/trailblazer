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

    ### Define output dict
    outdata = {
        'analysis_sex': {}, 
        'family': None,
        'duplicates': {},
        'genome_build': None,
        'mapped_reads': {},
        'mip_version': None,
        'sample_ids': [],
    }
    ### Config 
    ## Parse raw mip_config into dict
    config_data = files.parse_config(mip_config_raw)

    ## Add family id
    outdata['family'] = config_data['family']

    ## Add all samples from mip config
    for sample_data in config_data['samples']:
        outdata['sample_ids'].append(sample_data['id'])

    ### Qc metrics
    ## Parse qc metric file into dict
    qcmetrics_data = files.parse_qcmetrics(qcmetrics_raw)

    ## Add sample level info from qc_metric file
    for sample_data in qcmetrics_data['samples']:
         duplicates_percent = sample_data['duplicates'] * 100
         outdata['duplicates'][sample_data['id']] = f"{duplicates_percent:.3f}%"

         ## Add mapped reads
         mapped_reads_percent = sample_data['mapped'] * 100
         outdata['mapped_reads'][sample_data['id']] = f"{mapped_reads_percent:.3f}%"
            
         ## Add predicted sex
         outdata['analysis_sex'][sample_data['id']] = sample_data['predicted_sex']

    ### Qc sample info
    ## Parse qc sample info file
    sampleinfo_data = files.parse_sampleinfo(sampleinfo_raw)

    ## Add mip version
    outdata['mip_version'] = sampleinfo_data['version']
    
    ## Add mip version
    outdata['genome_build'] = sampleinfo_data['genome_build']

    return outdata
