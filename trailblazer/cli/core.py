# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import subprocess

import click
import coloredlogs
import ruamel.yaml

import trailblazer
from trailblazer.store import Store
from trailblazer.store.models import STATUS_OPTIONS
from trailblazer.log import LogAnalysis
from trailblazer.mip.start import MipCli
from trailblazer.mip.files import parse_config
from trailblazer.mip.sacct import parse_sacct
from trailblazer.exc import MissingFileError, MipStartError
from .utils import environ_email

log = logging.getLogger(__name__)


@click.group()
@click.option('-c', '--config', type=click.File())
@click.option('-d', '--database', help='path/URI of the SQL database')
@click.option('-r', '--root', help='families root directory')
@click.option('-l', '--log-level', default='INFO')
@click.version_option(trailblazer.__version__, prog_name=trailblazer.__title__)
@click.pass_context
def base(context, config, database, root, log_level):
    """Trailblazer - Simplify running MIP!"""
    coloredlogs.install(level=log_level)

    context.obj = ruamel.yaml.safe_load(config) if config else {}
    context.obj['database'] = database or context.obj.get('database')
    context.obj['root'] = root or context.obj.get('root')


@base.command('log')
@click.option('-s', '--sampleinfo', type=click.Path(exists=True), help='sample info file')
@click.option('-a', '--sacct', type=click.Path(exists=True), help='sacct job info file')
@click.option('-q', '--quiet', is_flag=True, help='supress outputs')
@click.argument('config', type=click.File())
@click.pass_context
def log_cmd(context, sampleinfo, sacct, quiet, config):
    """Log an analysis.

    CONFIG: MIP config file for an analysis
    """
    store = Store(context.obj['database'])
    log_analysis = LogAnalysis(store)
    try:
        new_run = log_analysis(config, sampleinfo=sampleinfo, sacct=sacct)
    except MissingFileError as error:
        click.echo(click.style(f"Skipping, missing Sacct file: {error.message}", fg='yellow'))
        return
    if new_run is None:
        if not quiet:
            click.echo(click.style('Analysis already logged', fg='yellow'))
    else:
        message = f"New log added: {new_run.family} ({new_run.id}) - {new_run.status}"
        click.echo(click.style(message, fg='green'))


@base.command()
@click.option('-c', '--mip-config', type=click.Path(exists=True), help='MIP config')
@click.option('-e', '--email', help='email for logging user')
@click.option('-p', '--priority', type=click.Choice(['low', 'normal', 'high']), default='normal')
@click.option('-d', '--dryrun', is_flag=True, help='only generate SBATCH scripts')
@click.option('--command', is_flag=True, help='only show the MIP command')
@click.argument('family', required=False)
@click.pass_context
def start(context, mip_config, email, priority, dryrun, command, family):
    """Start a new analysis."""
    store = Store(context.obj['database'])
    mip_cli = MipCli(context.obj['script'])
    mip_config = mip_config or context.obj['mip_config']
    email = email or environ_email()
    kwargs = dict(config=mip_config, family=family, priority=priority, email=email, dryrun=dryrun)
    if command:
        mip_command = mip_cli.build_command(**kwargs)
        click.echo(' '.join(mip_command))
    else:
        try:
            mip_cli(**kwargs)
            if not dryrun:
                store.add_pending(family, email=email)
        except MipStartError as error:
            click.echo(click.style(error.message, fg='red'))


@base.command()
@click.option('-s', '--status', type=click.Choice(STATUS_OPTIONS))
@click.pass_context
def ls(context, status):
    """Display recent logs for analyses."""
    store = Store(context.obj['database'])
    runs = store.analyses(status=status, deleted=False).limit(30)
    for run_obj in runs:
        click.echo(run_obj.family)


@base.command()
@click.option('-t', '--temporary', is_flag=True, help='delete all temporary logs')
@click.argument('analysis_id', type=int, required=False)
@click.pass_context
def delete(context, temporary, analysis_id):
    """Delete an analysis log from the database."""
    store = Store(context.obj['database'])
    if temporary:
        analysis_ids = (analysis_obj.id for analysis_obj in store.analyses(temp=True))
    elif analysis_id:
        analysis_ids = [analysis_id]
    else:
        click.echo(click.style('you need to provide an analysis ID', fg='yellow'))
        context.abort()

    for analysis_id in analysis_ids:
        analysis_obj = store.analysis(analysis_id)
        if analysis_obj is None:
            click.echo(click.style('analysis log not found', fg='red'))
            context.abort()
        analysis_obj.delete()
        store.commit()
        click.echo(f"analysis log deleted: {analysis_obj.family}")


@base.command()
@click.option('--reset', is_flag=True, help='reset database before setting up tables')
@click.option('--force', is_flag=True, help='bypass manual confirmations')
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    store = Store(context.obj['database'])
    existing_tables = store.engine.table_names()
    if force or reset:
        if existing_tables and not force:
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
@click.argument('root_dir', type=click.Path(exists=True), required=False)
@click.pass_context
def scan(context, root_dir):
    """Scan a directory for analyses."""
    store = Store(context.obj['database'])
    root_dir = root_dir or context.obj['root']
    config_files = Path(root_dir).glob('*/analysis/*_config.yaml')
    for config_file in config_files:
        log.debug("found analysis config: %s", config_file)
        with config_file.open() as stream:
            context.invoke(log_cmd, config=stream, quiet=True)

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


@base.command()
@click.option('-j', '--jobs', is_flag=True, help='only print job ids')
@click.argument('analysis_id', type=int)
@click.pass_context
def cancel(context, jobs, analysis_id):
    """Cancel all jobs in a run."""
    store = Store(context.obj['database'])
    analysis_obj = store.analysis(analysis_id)
    if analysis_obj is None:
        click.echo('analysis not found')
        context.abort()
    elif analysis_obj.status != 'running':
        click.echo(f"analysis not running: {analysis_obj.status}")
        context.abort()

    config_path = Path(analysis_obj.config_path)
    with config_path.open() as config_stream:
        config_raw = ruamel.yaml.safe_load(config_stream)
    config_data = parse_config(config_raw)

    log_path = Path(f"{config_data['log_path']}")
    if not log_path.exists():
        click.echo(f"missing MIP log file: {log_path}")
        context.abort()

    with log_path.open() as log_stream:
        # grep out all lines with scancel example
        id_rows = [line for line in log_stream if 'scancel' in line]
        job_ids = [id_row.strip()[-7:-1] for id_row in id_rows]

    if jobs:
        for job_id in job_ids:
            click.echo(job_id)
    else:
        for job_id in job_ids:
            log.debug(f"cancelling job: {job_id}")
            process = subprocess.Popen(['scancel', job_id])
            process.wait()

        click.echo('cancelled analysis successfully!')
