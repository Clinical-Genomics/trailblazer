# -*- coding: utf-8 -*-


def test_build_command(mip_cli):
    # GIVEN just a config
    mip_config = 'tests/fixtures/global_config.yaml'
    # WHEN building the MIP command
    mip_command = mip_cli.build_command(mip_config)
    # THEN it should use the correct options
    assert mip_command == ['perl', mip_cli.script, '--config_file', mip_config]
