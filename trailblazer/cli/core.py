import logging
import sys
from datetime import datetime
from pathlib import Path

import click
import coloredlogs
from sqlalchemy.orm import scoped_session

import trailblazer
from trailblazer.cli.utils.ls_helper import _get_ls_analysis_message
from trailblazer.cli.utils.user_helper import is_existing_user, is_user_archived
from trailblazer.constants import TRAILBLAZER_TIME_STAMP, FileFormat, TrailblazerStatus
from trailblazer.environ import environ_email
from trailblazer.io.controller import ReadFile
from trailblazer.models import Config
from trailblazer.store.database import get_session, initialize_database
from trailblazer.store.models import Analysis, User
from trailblazer.store.store import Store

LOG = logging.getLogger(__name__)
LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]


class DatabaseResource:
    """
    Setup the database and ensure resources are released when the
    CLI command has been processed.
    """

    def __init__(self, db_uri: str):
        self.db_uri = db_uri

    def __enter__(self):
        initialize_database(self.db_uri)

    def __exit__(self, _, __, ___):
        session: scoped_session = get_session()
        session.remove()


@click.group()
@click.option("-c", "--config", required=True, type=click.File())
@click.option(
    "-l", "--log-level", type=click.Choice(LEVELS), default="INFO", help="lowest level to log at"
)
@click.option("--verbose", is_flag=True, help="Show full log information, time stamp etc")
@click.version_option(trailblazer.__version__, prog_name=trailblazer.__title__)
@click.pass_context
def base(
    context: click.Context,
    config: click.File,
    log_level: str,
    verbose: bool,
):
    """Trailblazer - Monitor analyses"""
    if verbose:
        log_format = "%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s"
    else:
        log_format = "%(message)s" if sys.stdout.isatty() else None

    coloredlogs.install(level=log_level, fmt=log_format)

    validated_config = Config(
        **ReadFile.get_content_from_file(file_format=FileFormat.YAML, file_path=Path(config.name))
    )
    context.obj = dict(validated_config)
    context.with_resource(DatabaseResource(validated_config.database_url))
    context.obj["trailblazer_db"] = Store()


@base.command()
@click.option("--reset", is_flag=True, help="reset database before setting up tables")
@click.option("--force", is_flag=True, help="bypass manual confirmations")
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    existing_tables = context.obj["trailblazer_db"].engine.table_names()
    if force or reset:
        if existing_tables and not force:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg="yellow"), abort=True)
        context.obj["trailblazer_db"].drop_all()
    elif existing_tables:
        LOG.warning("Database already exists, use '--reset'")
        context.abort()
    context.obj["trailblazer_db"].setup()
    LOG.info(f"Success! New tables: {', '.join(context.obj['trailblazer'].engine.table_names())}")


@base.command()
@click.pass_context
def scan(context):
    """Scan ongoing analyses in SLURM"""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    trailblazer_db.update_ongoing_analyses()
    LOG.info("All analyses updated!")


@base.command("update-analysis")
@click.argument("analysis_id")
@click.pass_context
def update_analysis(context, analysis_id: int):
    """Update status of a single analysis."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    trailblazer_db.update_run_status(analysis_id=analysis_id)


@base.command("add-user")
@click.option("--name", help="Name of new user to add")
@click.argument("email", default=environ_email())
@click.pass_context
def add_user_to_db(context, email: str, name: str) -> None:
    """Add a new user to the database."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    existing_user = trailblazer_db.get_user(email=email, exclude_archived=False)
    if is_existing_user(user=existing_user, email=email):
        return
    new_user = trailblazer_db.add_user(email=email, name=name)
    LOG.info(f"New user added: {new_user.email} ({new_user.id})")


@base.command("get-user")
@click.argument("email", default=environ_email())
@click.pass_context
def get_user_from_db(context, email: str) -> None:
    """Display information about an existing user."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    existing_user = trailblazer_db.get_user(email=email, exclude_archived=False)
    if not is_existing_user(user=existing_user, email=email):
        return
    LOG.info(f"Existing user found: {existing_user.to_dict()}")


@base.command("get-users")
@click.option("--name", type=click.types.STRING, help="Name of new users to list")
@click.option("--email", type=click.types.STRING, help="Name of new users to list")
@click.option("--exclude-archived", is_flag=True, help="Exclude archived users")
@click.pass_context
def get_users_from_db(context, name: str, email: str, exclude_archived: bool) -> None:
    """Display information about existing users."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    users: list[User] = trailblazer_db.get_users(
        email=email, exclude_archived=exclude_archived, name=name
    )
    LOG.info("Listing users in database:")
    for user in users:
        LOG.info(f"{user.to_dict()}")


@base.command("archive-user")
@click.argument("email", default=environ_email())
@click.pass_context
def archive_user(context, email: str) -> None:
    """Archive an existing user identified by email."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    existing_user: User = trailblazer_db.get_user(email=email, exclude_archived=False)

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
    trailblazer_db: Store = context.obj["trailblazer_db"]
    existing_user: User = trailblazer_db.get_user(email=email, exclude_archived=False)

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
    """Cancel all jobs in an analysis."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    try:
        trailblazer_db.cancel_ongoing_analysis(analysis_id=analysis_id, email=environ_email())
    except Exception as error:
        LOG.error(error)


@base.command("set-completed")
@click.argument("analysis_id", type=int)
@click.pass_context
def set_analysis_completed(context, analysis_id):
    """Set status of an analysis to 'COMPLETED'."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    try:
        trailblazer_db.update_analysis_status_to_completed(analysis_id=analysis_id)
    except Exception as error:
        LOG.error(error)


@base.command("set-status")
@click.option(
    "--status",
    is_flag=False,
    type=str,
    help=f"Status to be set. Can take the values:{TrailblazerStatus.statuses()}",
)
@click.argument("case_id", type=str)
@click.pass_context
def set_analysis_status(
    context,
    case_id: str,
    status: str,
):
    """Set the status of the latest analysis for a given case id."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    try:
        trailblazer_db.update_analysis_status(case_id=case_id, status=status)
    except ValueError as error:
        LOG.error(error)
        raise click.Abort from error
    except Exception as error:
        LOG.error(error)


@base.command()
@click.option("--force", is_flag=True, help="Force delete if analysis is ongoing")
@click.option("--cancel-jobs", is_flag=True, help="Cancel all ongoing jobs before deleting")
@click.argument("analysis_id", type=int)
@click.pass_context
def delete(context, analysis_id: int, force: bool, cancel_jobs: bool):
    """Delete analysis completely from database, and optionally cancel all ongoing analysis jobs."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    try:
        if cancel_jobs:
            trailblazer_db.cancel_ongoing_analysis(analysis_id=analysis_id)
        trailblazer_db.delete_analysis(analysis_id=analysis_id, force=force)
    except Exception as error:
        LOG.error(error)


@base.command("ls")
@click.option(
    "-s",
    "--status",
    type=click.Choice(TrailblazerStatus.statuses()),
    help="Find analysis with specified status",
)
@click.option("-b", "--before", type=str, help="Find analyses started before date")
@click.option("-c", "--comment", type=str, help="Find analysis with comment")
@click.option("--limit", type=int, default=30, help="Limit the number of analysis returned")
@click.pass_context
def ls_cmd(context, before: str, status: TrailblazerStatus, comment: str, limit: int = 30):
    """Display recent logs for the latest analyses."""
    trailblazer_db: Store = context.obj["trailblazer_db"]
    analyses: list[Analysis] | None = trailblazer_db.get_analyses_by_status_started_at_and_comment(
        status=status,
        before=datetime.strptime(before, TRAILBLAZER_TIME_STAMP).date() if before else None,
        comment=comment,
    )
    if analyses:
        for analysis in analyses[:limit]:
            (message, color) = _get_ls_analysis_message(analysis=analysis)
            click.echo(click.style(message, fg=color))
    else:
        LOG.warning("No analyses matching search criteria")
