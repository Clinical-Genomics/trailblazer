from functools import partial

import pytest
from click.testing import CliRunner

from trailblazer.cli import base


@pytest.fixture
def cli_runner() -> CliRunner:
    """Return a CliRunner fixture."""
    return CliRunner()


@pytest.fixture
def invoke_cli(cli_runner: CliRunner) -> partial:
    """Invokes CLI base with partial functionality."""
    return partial(cli_runner.invoke, base)
