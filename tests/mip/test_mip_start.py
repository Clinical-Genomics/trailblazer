# -*- coding: utf-8 -*-


def test_build_command(mip_cli):
    # GIVEN just a config
    mip_config = 'tests/fixtures/global_config.yaml'
    # WHEN building the MIP command
    mip_command = mip_cli.build_command(mip_config)
    # THEN it should use the correct options
    assert mip_command == ['perl', mip_cli.script, '--config_file', mip_config]


def test_build_command_with_default(mip_cli):
    # GIVEN a supported option with a default
    option = '--dry_run_all'
    default = '2'
    # WHEN building a MIP command
    mip_command = mip_cli.build_command('test/mip.conf', dryrun=True)
    # THEN it should pick the right command and choose the default
    assert option in mip_command
    assert mip_command[mip_command.index(option) + 1] == default


def test_build_command_without_default(mip_cli):
    # GIVEN a supported option without a default
    option = '--slurm_quality_of_service'
    value = 'high'
    # WHEN building a MIP command
    mip_command = mip_cli.build_command('test/mip.conf', priority=value)
    # THEN it should pick the right command and choose the default
    assert option in mip_command
    assert mip_command[mip_command.index(option) + 1] == value
