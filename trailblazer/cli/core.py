import logging
from pathlib import Path
import subprocess

import click
import coloredlogs
import ruamel.yaml

import trailblazer
from trailblazer.cli.get import get
from trailblazer.store import Store
from .ls import ls_cmd

LOG = logging.getLogger(__name__)


@click.group()
@click.option("-c", "--config", type=click.File())
@click.option("-d", "--database", help="path/URI of the SQL database")
@click.option("-r", "--root", help="families root directory")
@click.option("-l", "--log-level", default="INFO")
@click.version_option(trailblazer.__version__, prog_name=trailblazer.__title__)
@click.pass_context
def base(context, config, database, root, log_level):
    """Trailblazer - Simplify running MIP!"""
    coloredlogs.install(level=log_level)

    context.obj = ruamel.yaml.safe_load(config) if config else {}
    context.obj["database"] = database or context.obj.get("database")
    context.obj["root"] = root or context.obj.get("root")
    context.obj["store"] = Store(context.obj["database"])


@base.command()
@click.option("--reset", is_flag=True, help="reset database before setting up tables")
@click.option("--force", is_flag=True, help="bypass manual confirmations")
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    existing_tables = context.obj["store"].engine.table_names()
    if force or reset:
        if existing_tables and not force:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg="yellow"), abort=True)
        context.obj["store"].drop_all()
    elif existing_tables:
        click.echo(click.style("Database already exists, use '--reset'", fg="red"))
        context.abort()

    context.obj["store"].setup()
    message = f"Success! New tables: {', '.join(context.obj['store'].engine.table_names())}"
    click.echo(click.style(message, fg="green"))


@base.command()
@click.pass_context
def scan(context):
    """Scan a directory for analyses."""
    context.obj["store"].update_run_status()


@base.command()
@click.option("--name", help="Name of new user to add")
@click.argument("email")
@click.pass_context
def user(context, name, email):
    """Add a new or display information about an existing user."""
    existing_user = context.obj["store"].user(email)
    if existing_user:
        click.echo(existing_user.to_dict())
    elif name:
        new_user = context.obj["store"].add_user(name, email)
        click.echo(click.style(f"New user added: {email} ({new_user.id})", fg="green"))
    else:
        click.echo(click.style("User not found", fg="yellow"))


@base.command()
@click.option("-j", "--jobs", is_flag=True, help="only print job ids")
@click.argument("analysis_id", type=int)
@click.pass_context
def cancel(context, jobs, analysis_id):
    """Cancel all jobs in a run."""
    analysis_obj = context.obj["store"].analysis(analysis_id)
    if analysis_obj is None:
        click.echo("analysis not found")
        context.abort()
    elif analysis_obj.status != "running":
        click.echo(f"analysis not running: {analysis_obj.status}")
        context.abort()

    config_path = Path(analysis_obj.config_path)
    config_data = ruamel.yaml.safe_load(open(config_path))
    log_path = Path(config_data.get("log_path"))
    if not log_path.exists():
        click.echo(f"missing MIP log file: {log_path}")
        context.abort()

    with log_path.open() as log_stream:
        all_jobs = job_ids(log_stream)

    if jobs:
        for job_id in all_jobs:
            click.echo(job_id)
    else:
        for job_id in all_jobs:
            LOG.debug(f"cancelling job: {job_id}")
            process = subprocess.Popen(["scancel", job_id])
            process.wait()

        analysis_obj.status = "canceled"
        context.obj["store"].commit()
        click.echo("cancelled analysis successfully!")


base.add_command(ls_cmd)
base.add_command(get)
