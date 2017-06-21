# -*- coding: utf-8 -*-
import logging
from pathlib import Path

import click
import coloredlogs
import ruamel.yaml

import trailblazer
from trailblazer.store import Store
from trailblazer.log import LogAnalysis
from trailblazer.mip.start import MipCli
from .utils import environ_email

log = logging.getLogger(__name__)


@click.group()
@click.option('-c', '--config', type=click.File())
@click.option('-d', '--database', help='path/URI of the SQL database')
@click.option('-l', '--log-level', default='INFO')
@click.version_option(trailblazer.__version__, prog_name=trailblazer.__title__)
@click.pass_context
def base(context, config, database, log_level):
    """Trailblazer - Simplify running MIP!"""
    coloredlogs.install(level=log_level)

    context.obj = ruamel.yaml.safe_load(config) if config else {}
    if database:
        context.obj['database'] = database


@base.command('log')
@click.option('-s', '--sampleinfo', type=click.Path(exists=True), help='sample info file')
@click.option('-a', '--sacct', type=click.Path(exists=True), help='sacct job info file')
@click.argument('config', type=click.File())
@click.pass_context
def log_cmd(context, sampleinfo, sacct, config):
    """Log an analysis.

    CONFIG: MIP config file for an analysis
    """
    store = Store(context.obj['database'])
    log_analysis = LogAnalysis(store)
    new_run = log_analysis(config, sampleinfo=sampleinfo, sacct=sacct)
    if new_run is None:
        click.echo(click.style('Analysis already logged', fg='yellow'))
    else:
        message = f"New log added: {new_run.family} ({new_run.id}) - {new_run.status}"
        click.echo(click.style(message, fg='green'))


@base.command()
@click.option('-c', '--config', type=click.Path(exists=True), help='MIP config')
@click.option('-e', '--email', help='email for logging user')
@click.option('--command', is_flag=True, help='only show the MIP command')
@click.argument('family', required=False)
@click.pass_context
def start(context, config, email, command, family):
    """Start a new analysis."""
    store = Store(context.obj['database'])
    mip_cli = MipCli(context.obj['script'])
    config = config or context.obj['config']
    mip_cli(config, family)
    store.add_pending(family, email=(email or environ_email()))


@base.command()
@click.pass_context
def ls(context):
    """Display recent logs for analyses."""
    store = Store(context.obj['database'])
    runs = store.analyses(status='completed', deleted=False).limit(30)
    for run_obj in runs:
        click.echo(run_obj.family)


@base.command()
@click.argument('analysis_id', type=int)
@click.pass_context
def delete(context, analysis_id):
    """Delete an analysis log from the database."""
    store = Store(context.obj['database'])
    analysis_obj = store.analysis(analysis_id)
    if analysis_obj is None:
        click.echo(click.style('analysis log not found', fg='red'))
        context.abort()
    analysis_obj.delete()
    store.commit()
    click.echo(f"analysis log deleted: {analysis_obj.family}")


@base.command()
@click.option('--reset', is_flag=True, help='reset database before setting up tables')
@click.pass_context
def init(context, reset):
    """Setup the database."""
    store = Store(context.obj['database'])
    existing_tables = store.engine.table_names()
    if reset:
        if existing_tables:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg='yellow'), abort=True)
        store.drop_all()
    elif existing_tables:
        click.echo(click.style("Database already exists, use '--reset'", fg='red'))
        context.abort()

    store.setup()
    message = f"Success! New tables: {', '.join(store.engine.table_names())}"
    click.echo(click.style(message, fg='green'))


@base.command()
@click.argument('root_dir', type=click.Path(exists=True))
@click.pass_context
def scan(context, root_dir):
    """Scan a directory for analyses."""
    store = Store(context.obj['database'])
    config_files = Path(root_dir).glob('*/analysis/*_config.yaml')
    for config_file in config_files:
        log.debug("adding analysis: %s", config_file)
        with config_file.open() as stream:
            context.invoke(log_cmd, config=stream)

    store.track_update()


@base.command()
@click.option('--name', help='Name of new user to add')
@click.argument('email')
@click.pass_context
def user(context, name, email):
    """Add a new or display information about an existing user."""
    store = Store(context.obj['database'])
    existing_user = store.user(email)
    if existing_user:
        click.echo(existing_user.to_dict())
    elif name:
        new_user = store.add_user(name, email)
        click.echo(click.style(f"New user added: {email} ({new_user.id})", fg='green'))
    else:
        click.echo(click.style('User not found', fg='yellow'))
