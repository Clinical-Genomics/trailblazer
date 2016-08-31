# -*- coding: utf-8 -*-
import yaml

from trailblazer.analyze import restart


def test_update_maxgaussian(tmp_config):
    # GIVEN a config of a started analysis
    before = yaml.load(tmp_config.open())
    assert before['GATKVariantReCalibrationSnvMaxGaussians'] == '0'
    # WHEN updating it for a restart after a GATK error
    restart.update_maxgaussian(str(tmp_config))
    # THEN it should update the max gaussian flag and programs
    after = yaml.load(tmp_config.open())
    assert after['GATKVariantReCalibrationSnvMaxGaussians'] == 1
