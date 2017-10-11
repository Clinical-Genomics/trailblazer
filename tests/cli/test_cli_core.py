# -*- coding: utf-8 -*-
import trailblazer


def test_base(invoke_cli):
    # GIVEN the cli
    # WHEN asking for the version
    result = invoke_cli(['--version'])
    # THEN it should print the name and version of the tool only
    assert trailblazer.__title__ in result.output
    assert trailblazer.__version__ in result.output
