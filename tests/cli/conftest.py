from functools import partial

import pytest
from click.testing import CliRunner

from trailblazer.cli import base


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, base)
