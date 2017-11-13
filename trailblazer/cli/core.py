# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import subprocess

import click
import coloredlogs
import ruamel.yaml

import trailblazer
from trailblazer.store import Store
from trailblazer.log import LogAnalysis
from trailblazer.mip.start import MipCli
from trailblazer.mip.files import parse_config
from trailblazer.mip.miplog import job_ids
from trailblazer.exc import MissingFileError, MipStartError
from .utils import environ_email
from .clean import clean
from .delete import delete
from .ls import ls_cmd
from .check import check

LOG = logging.getLogger(__name__)


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
    context.obj['store'] = Store(context.obj['database'], context.obj['root'])


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
    log_analysis = LogAnalysis(context.obj['store'])
    try:
        new_run = log_analysis(config, sampleinfo=sampleinfo, sacct=sacct)
    except MissingFileError as error:
        click.echo(click.style(f"Skipping, missing Sacct file: {error.message}", fg='yellow'))
        return
    except KeyError as error:
        print(click.style(f"unexpected output, missing key: {error.args[0]}", fg='yellow'))
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
                context.obj['store'].add_pending(family, email=email)
        except MipStartError as error:
            click.echo(click.style(error.message, fg='red'))


@base.command()
@click.option('--reset', is_flag=True, help='reset database before setting up tables')
@click.option('--force', is_flag=True, help='bypass manual confirmations')
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    existing_tables = context.obj['store'].engine.table_names()
    if force or reset:
        if existing_tables and not force:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg='yellow'), abort=True)
        context.obj['store'].drop_all()
    elif existing_tables:
        click.echo(click.style("Database already exists, use '--reset'", fg='red'))
        context.abort()

    context.obj['store'].setup()
    message = f"Success! New tables: {', '.join(context.obj['store'].engine.table_names())}"
    click.echo(click.style(message, fg='green'))


@base.command()
@click.argument('root_dir', type=click.Path(exists=True), required=False)
@click.pass_context
def scan(context, root_dir):
    """Scan a directory for analyses."""
    root_dir = root_dir or context.obj['root']
    config_files = Path(root_dir).glob('*/analysis/*_config.yaml')
    for config_file in config_files:
        LOG.debug("found analysis config: %s", config_file)
        with config_file.open() as stream:
            context.invoke(log_cmd, config=stream, quiet=True)

    context.obj['store'].track_update()


@base.command()
@click.option('--name', help='Name of new user to add')
@click.argument('email')
@click.pass_context
def user(context, name, email):
    """Add a new or display information about an existing user."""
    existing_user = context.obj['store'].user(email)
    if existing_user:
        click.echo(existing_user.to_dict())
    elif name:
        new_user = context.obj['store'].add_user(name, email)
        click.echo(click.style(f"New user added: {email} ({new_user.id})", fg='green'))
    else:
        click.echo(click.style('User not found', fg='yellow'))


@base.command()
@click.option('-j', '--jobs', is_flag=True, help='only print job ids')
@click.argument('analysis_id', type=int)
@click.pass_context
def cancel(context, jobs, analysis_id):
    """Cancel all jobs in a run."""
    analysis_obj = context.obj['store'].analysis(analysis_id)
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
        all_jobs = job_ids(log_stream)

    if jobs:
        for job_id in all_jobs:
            click.echo(job_id)
    else:
        for job_id in all_jobs:
            LOG.debug(f"cancelling job: {job_id}")
            process = subprocess.Popen(['scancel', job_id])
            process.wait()

        analysis_obj.status = 'canceled'
        context.obj['store'].commit()
        click.echo('cancelled analysis successfully!')


base.add_command(delete)
base.add_command(ls_cmd)
base.add_command(clean)
base.add_command(check)
