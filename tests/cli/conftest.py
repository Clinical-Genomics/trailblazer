from functools import partial

import pytest
from click.testing import CliRunner

from trailblazer.cli.core import base

from trailblazer.containers import Container
from trailblazer.server.wiring import setup_dependency_injection


@pytest.fixture(scope="session")
def process_exit_success() -> int:
    """Return the exit code for a successful process."""
    return 0


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    """Return a CliRunner fixture."""
    return CliRunner()


@pytest.fixture(scope="session")
def invoke_cli(cli_runner: CliRunner) -> partial:
    """Invokes CLI base with partial functionality."""
    return partial(cli_runner.invoke, base)


@pytest.fixture(autouse=True)
def container() -> Container:
    container: Container = setup_dependency_injection()
    return container
