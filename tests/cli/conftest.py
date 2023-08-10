from functools import partial

import pytest
from click.testing import CliRunner

from trailblazer.cli.core import base


@pytest.fixture(name="process_exit_success", scope="session")
def fixture_process_exit_success() -> int:
    """Return the exit code for a successful process."""
    return 0


@pytest.fixture(name="cli_runner", scope="session")
def fixture_cli_runner() -> CliRunner:
    """Return a CliRunner fixture."""
    return CliRunner()


@pytest.fixture(name="invoke_cli", scope="session")
def fixture_invoke_cli(cli_runner: CliRunner) -> partial:
    """Invokes CLI base with partial functionality."""
    return partial(cli_runner.invoke, base)
