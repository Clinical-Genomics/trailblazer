# -*- coding: utf-8 -*-
from trailblazer.analyze import start


def test_start_mip():
    # GIVEN you want to start MIP with:
    kwargs = dict(
        analysis_type='genomes',
        family_id='16105',
        customer='cust003',
        ccp='/tmp/cust003/16105',
        gene_list='cust003-NMD.txt',
        config='/tmp/mip_config.yaml',
    )
    # WHEN generating a start script
    script = start.start_mip(**kwargs)
    # THEN it should build a corresponding command
    assert "--analysisType {}".format(kwargs['analysis_type']) in script
    assert "--configFile {}".format(kwargs['config']) in script
    assert "--familyID {}".format(kwargs['family_id']) in script
    assert "--instanceTag {}".format(kwargs['customer']) in script
    assert "--vcfParserSelectFile {}".format(kwargs['gene_list']) in script
    assert "--clusterConstantPath {}".format(kwargs['ccp']) in script


def test_start_mip_with_config():
    pass
    # GIVEN an existing config
    existing_config = '/tmp/16105_config.yaml'
    # WHEN you build a start script with just the config
    script = start.start_mip(analysis_config=existing_config)
    # THEN it should construct a simple command
    mip_command = "\nperl mip.pl --config {}".format(existing_config)
    assert script.endswith(mip_command)
