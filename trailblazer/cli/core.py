import logging
import sys
from pathlib import Path
from typing import List

import click
import coloredlogs
from dateutil.parser import parse as parse_date

import trailblazer
from trailblazer.cli.utils.user_helper import is_existing_user, is_user_archived
from trailblazer.constants import FileFormat
from trailblazer.environ import environ_email
from trailblazer.io.controller import ReadFile
from trailblazer.store.api import Store
from trailblazer.store.models import STATUS_OPTIONS, User

LOG = logging.getLogger(__name__)
LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]


@click.group()
@click.option("-c", "--config", type=click.File())
@click.option("-d", "--database", help="path/URI of the SQL database")
@click.option(
    "-l", "--log-level", type=click.Choice(LEVELS), default="INFO", help="lowest level to log at"
)
@click.option("--verbose", is_flag=True, help="Show full log information, time stamp etc")
@click.version_option(trailblazer.__version__, prog_name=trailblazer.__title__)
@click.pass_context
def base(
    context,
    config,
    database,
    log_level: str,
    verbose: bool,
):
    """Trailblazer - Monitor analyses"""
    if verbose:
        log_format = "%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s"
    else:
        log_format = "%(message)s" if sys.stdout.isatty() else None

    coloredlogs.install(level=log_level, fmt=log_format)

    context.obj = (
        ReadFile.get_content_from_file(file_format=FileFormat.YAML, file_path=Path(config.name))
        if config
        else {}
    )
    context.obj["database"] = database or context.obj.get("database", "sqlite:///:memory:")
    context.obj["trailblazer"] = Store(context.obj["database"])


@base.command()
@click.option("--reset", is_flag=True, help="reset database before setting up tables")
@click.option("--force", is_flag=True, help="bypass manual confirmations")
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    existing_tables = context.obj["trailblazer"].engine.table_names()
    if force or reset:
        if existing_tables and not force:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg="yellow"), abort=True)
        context.obj["trailblazer"].drop_all()
    elif existing_tables:
        LOG.warning("Database already exists, use '--reset'")
        context.abort()
    context.obj["trailblazer"].setup()
    LOG.info(f"Success! New tables: {', '.join(context.obj['trailblazer'].engine.table_names())}")


@base.command()
@click.pass_context
def scan(context):
    """Scan ongoing analyses in SLURM"""
    context.obj["trailblazer"].update_ongoing_analyses()
    LOG.info("All analyses updated!")


@base.command("update-analysis")
@click.argument("analysis_id")
@click.pass_context
def update_analysis(context, analysis_id: int):
    """Update status of a single analysis"""
    context.obj["trailblazer"].update_run_status(analysis_id=analysis_id)


@base.command()
@click.option("--name", help="Name of new user to add")
@click.argument("email", default=environ_email())
@click.pass_context
def user(context, name: str, email: str) -> None:
    """Add a new or display information about an existing user."""
    trailblazer_db: Store = context.obj["trailblazer"]
    existing_user = trailblazer_db.user(email, include_archived=True)
    if existing_user:
        LOG.info(f"Existing user found: {existing_user.to_dict()}")
    elif name:
        new_user = trailblazer_db.add_user(email=email, name=name)
        LOG.info(f"New user added: {email} ({new_user.id})")
    else:
        LOG.error("User not found")


@base.command("users")
@click.option("--name", type=click.types.STRING, help="Name of new users to list")
@click.option("--email", type=click.types.STRING, help="Name of new users to list")
@click.option("--exclude-archived", is_flag=True, help="Exclude archived users")
@click.pass_context
def get_users_from_db(context, name: str, email: str, exclude_archived: bool) -> None:
    """Display information about existing users."""
    trailblazer_db: Store = context.obj["trailblazer"]
    users: List[User] = trailblazer_db.get_users(
        email=email, exclude_archived=exclude_archived, name=name
    )

    LOG.info("Listing users in database:")
    for user in users:
        LOG.info(f"{user}")


@base.command("archive-user")
@click.argument("email", default=environ_email())
@click.pass_context
def archive_user(context, email: str) -> None:
    """Archive an existing user identified by email."""
    trailblazer_db: Store = context.obj["trailblazer"]
    existing_user: user = trailblazer_db.user(email=email, include_archived=True)

    if not is_existing_user(user=existing_user, email=email):
        return
    if is_user_archived(user=existing_user, email=email):
        return

    trailblazer_db.update_user_is_archived(user=existing_user, archive=True)
    LOG.info(f"User archived: {email}")


@base.command("unarchive-user")
@click.argument("email", default=environ_email())
@click.pass_context
def unarchive_user(context, email: str) -> None:
    """Unarchive an existing user identified by email."""
    trailblazer_db: Store = context.obj["trailblazer"]
    existing_user: user = trailblazer_db.user(email=email, include_archived=True)

    if not is_existing_user(user=existing_user, email=email):
        return
    if not is_user_archived(user=existing_user, email=email):
        return

    trailblazer_db.update_user_is_archived(user=existing_user, archive=False)
    LOG.info(f"User unarchived: {email}")


@base.command()
@click.argument("analysis_id", type=int)
@click.pass_context
def cancel(context, analysis_id):
    """Cancel all jobs in a run."""
    try:
        context.obj["trailblazer"].cancel_analysis(analysis_id=analysis_id, email=environ_email())
    except Exception as e:
        LOG.error(e)


@base.command("set-completed")
@click.argument("analysis_id", type=int)
@click.pass_context
def set_analysis_completed(context, analysis_id):
    """Set status of an analysis to "COMPLETED" """
    try:
        context.obj["trailblazer"].set_analysis_completed(analysis_id=analysis_id)
    except Exception as e:
        LOG.error(e)


@base.command("set-status")
@click.option(
    "--status",
    is_flag=False,
    type=str,
    help=f"Status to be set. Can take the values:{STATUS_OPTIONS}",
)
@click.argument("case_id", type=str)
@click.pass_context
def set_analysis_status(
    context,
    case_id: str,
    status: str,
):
    """Set the status of the latest analysis for a given CASE_ID."""
    try:
        context.obj["trailblazer"].set_analysis_status(case_id=case_id, status=status)
    except ValueError as e:
        LOG.error(e)
        raise click.Abort from e
    except Exception as e:
        LOG.error(e)


@base.command()
@click.option("--force", is_flag=True, help="Force delete if analysis ongoing")
@click.option("--cancel-jobs", is_flag=True, help="Cancel all ongoing jobs before deleting")
@click.argument("analysis_id", type=int)
@click.pass_context
def delete(context, analysis_id: int, force: bool, cancel_jobs: bool):
    """Delete analysis completely from database, and optionally cancel all ongoing jobs"""
    try:
        if cancel_jobs:
            context.obj["trailblazer"].cancel_analysis(analysis_id=analysis_id)

        context.obj["trailblazer"].delete_analysis(analysis_id=analysis_id, force=force)
    except Exception as e:
        LOG.error(e)


@base.command("ls")
@click.option(
    "-s", "--status", type=click.Choice(STATUS_OPTIONS), help="Find analysis with specified status"
)
@click.option("-b", "--before", help="Find analyses started before date")
@click.option("-c", "--comment", help="Find analysis with comment")
@click.pass_context
def ls_cmd(context, before, status, comment):
    """Display recent logs for analyses."""
    runs = (
        context.obj["trailblazer"]
        .analyses(
            status=status,
            deleted=False,
            before=parse_date(before) if before else None,
            comment=comment,
        )
        .limit(30)
    )
    for run_obj in runs:
        if run_obj.status == "pending":
            message = f"{run_obj.id} | {run_obj.family} [{run_obj.status.upper()}]"
        else:
            message = (
                f"{run_obj.id} | {run_obj.family} {run_obj.started_at.date()} "
                f"[{run_obj.type.upper()}/{run_obj.status.upper()}]"
            )
            if run_obj.status == "running":
                message = click.style(f"{message} - {run_obj.progress * 100}/100", fg="blue")
            elif run_obj.status == "completed":
                message = click.style(f"{message} - {run_obj.completed_at}", fg="green")
            elif run_obj.status == "failed":
                message = click.style(message, fg="red")
        click.echo(message)
