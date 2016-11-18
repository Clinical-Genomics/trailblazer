# -*- coding: utf-8 -*-
"""
https://blog.nelhage.com/2010/02/a-very-subtle-bug/
"""
import logging
import os

import click
from path import Path

from . import restart as restart_api
from .start import start_mip, build_pending
from trailblazer.exc import AnalysisStartError
from trailblazer.store import api
from trailblazer.add.commit import commit_analysis

BRANCH_OPTIONS = restart_api.BRANCHES.keys()


log = logging.getLogger(__name__)


@click.group()
@click.pass_context
def analyze(context):
    """Interact with MIP command line interface."""
    pass


@analyze.command()
@click.option('-p', '--ccp', type=click.Path(exists=True))
@click.option('-a', '--analysis-type')
@click.option('-f', '--family', required=True)
@click.option('-c', '--config', type=click.Path(exists=True))
@click.option('-x', '--executable', type=click.Path(exists=True))
@click.option('-i', '--customer', required=True)
@click.option('-g', '--gene-list')
@click.option('-e', '--email', help='email to send errors to')
@click.option('--dryrun', is_flag=True)
@click.option('--conda-env')
@click.pass_context
def start(context, ccp, analysis_type, family, config, customer, gene_list,
          dryrun, executable, out, conda_env, email):
    """Start a new analysis."""
    # check if case is already running
    case_id = "{}-{}".format(customer, family)
    if api.is_running(case_id):
        log.error("case already running!")
        context.abort()

    config = config or context.obj['mip_config']
    executable = executable or context.obj['mip_exe']
    gene_list = gene_list or context.obj['mip_genelist']
    conda_env = conda_env or context.obj.get('conda_env')
    email = email or environ_email()
    ccp_abs = (Path(ccp).abspath() if ccp else
               Path(context.obj['analysis_root']).joinpath(customer, family))
    analysis_type = analysis_type or guess_analysis_type(ccp_abs)

    process = start_mip(
        analysis_type,
        family,
        config,
        ccp_abs,
        executable=executable,
        customer=customer,
        gene_list=gene_list,
        dryrun=dryrun,
        conda_env=conda_env,
        email=email
    )
    process.wait()
    if process.returncode != 0:
        log.error("error starting analysis, check the output")

    case_id = "{}-{}".format(customer, family)
    new_entry = build_pending(case_id, ccp_abs, analysis_type)
    commit_analysis(context.obj['manager'], new_entry)


@analyze.command()
@click.option('--max-gaussian', is_flag=True)
@click.option('-d', '--disable', type=click.Choice(BRANCH_OPTIONS),
              multiple=True)
@click.option('-s', '--start-from', type=click.Choice(restart_api.PROGRAMS))
@click.option('-e', '--extras', multiple=True, type=(unicode, unicode))
@click.option('--restart/--no-restart', default=True)
@click.option('-e', '--email', help='email to send errors to')
@click.option('-c', '--case', help='lookup analysis in database')
@click.argument('config_path', type=click.Path(exists=True), required=False)
@click.pass_context
def restart(context, max_gaussian, restart, email, case, extras, disable,
            start_from, config_path):
    """Restart MIP with modifications to the config file."""
    if not case and not config_path:
        log.error("you must provide either case of config path")
        context.abort()

    if case:
        most_recent = api.case(case).first()
        config_path = most_recent.config_path

    if max_gaussian:
        new_values = restart_api.update_maxgaussian(config_path)
    else:
        extras = dict(extras)
        new_values = restart_api.update_config(config_path,
                                               start_step=start_from,
                                               disable_branches=disable,
                                               **extras)

    log.info("update config: {}".format(config_path))
    restart_api.write_config(config_path, new_values)

    if restart:
        email = email or environ_email() or new_values.get('email')
        conda_env = context.obj.get('conda_env')
        kwargs = dict(executable=context.obj.get('mip_exe'), email=email,
                      conda_env=conda_env)
        process = start_mip(analysis_config=config_path, **kwargs)
        process.wait()
        if process.returncode != 0:
            log.error("error starting analysis, check the output")

        if case:
            new_entry = build_pending(most_recent.case_id,
                                      most_recent.root_dir,
                                      most_recent.type)
            commit_analysis(context.obj['manager'], new_entry)


def environ_email():
    """Guess email from sudo user environment variable."""
    username = os.environ.get('SUDO_USER')
    if username:
        return "{}@scilifelab.se".format(username)


def guess_analysis_type(family_root):
    """Guess analysis type based on folders."""
    input_folders = [directory.basename() for directory in
                     Path(family_root).listdir() if
                     directory.basename() in ('exomes', 'genomes')]
    if len(input_folders) > 1:
        return 'mixed'
    elif len(input_folders) == 1:
        return input_folders[0]
    else:
        raise AnalysisStartError("can't determine analysis type")
