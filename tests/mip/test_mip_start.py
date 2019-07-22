# -*- coding: utf-8 -*-


def test_build_command(mip_cli):
    # GIVEN just a config
    mip_config = 'tests/fixtures/global_config.yaml'
    case_id = 'angrybird'
    # WHEN building the MIP command
    mip_command = mip_cli.build_command(case=case_id, config=mip_config)
    # THEN it should use the correct options
    assert mip_command == [mip_cli.script, case_id, '--config_file', mip_config]


def test_build_command_with_default(mip_cli):
    # GIVEN a supported option with a default
    option = '--gatk_varrecal_snv_max_gau'
    default = '1'
    case_id = 'angrybird'
    # WHEN building a MIP command
    mip_command = mip_cli.build_command(case=case_id, config='test/mip.conf', max_gaussian=True)
    # THEN it should pick the right command and choose the default
    assert option in mip_command
    assert mip_command[mip_command.index(option) + 1] == default


def test_build_command_without_default(mip_cli):
    # GIVEN a supported option without a default
    option = '--slurm_quality_of_service'
    value = 'high'
    case_id = 'angrybird'
    # WHEN building a MIP command
    mip_command = mip_cli.build_command(case=case_id, config='test/mip.conf', priority=value)
    # THEN it should pick the right command and choose the default
    assert option in mip_command
    assert mip_command[mip_command.index(option) + 1] == value
