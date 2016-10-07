# -*- coding: utf-8 -*-
import logging

import click
from path import path

from . import restart as restart_api
from .start import start_mip, build_pending
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
@click.option('-p', '--ccp', type=click.Path(exists=True), required=True)
@click.option('-a', '--analysis-type', default='genomes')
@click.option('-f', '--family', required=True)
@click.option('-c', '--config', type=click.Path(exists=True))
@click.option('-x', '--executable', type=click.Path(exists=True))
@click.option('-i', '--customer', required=True)
@click.option('-g', '--gene-list')
@click.option('-e', '--email', help='email to send errors to')
@click.option('--dryrun', is_flag=True)
@click.option('-o', '--out', type=click.File('w'), default='-')
@click.option('--conda-env')
@click.option('--script-dir', type=click.Path(exists=True))
@click.pass_context
def start(context, ccp, analysis_type, family, config, customer, gene_list,
          dryrun, executable, out, conda_env, email, script_dir):
    """Start a new analysis."""
    config = config or context.obj['mip_config']
    executable = executable or context.obj['mip_exe']
    gene_list = gene_list or context.obj['mip_genelist']
    conda_env = conda_env or context.obj.get('conda_env')
    script_dir = script_dir or context.obj.get('script_dir')

    ccp_abs = path(ccp).abspath()
    script = start_mip(
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

    if script_dir:
        case_id = "{}-{}".format(customer, family)
        out_filename = "{}.sh".format(case_id)
        out_path = path(script_dir).joinpath(out_filename)
        click.echo(script, file=out_path.open('w'))
    else:
        click.echo(script, file=out)

    case_id = "{}-{}".format(customer, family)
    new_entry = build_pending(case_id, ccp_abs, analysis_type)
    commit_analysis(context.obj['manager'], new_entry)


@analyze.command()
@click.option('--max-gaussian')
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

    script_dir = context.obj.get('script_dir')
    if restart and script_dir:
        email = email or new_values.get('email')
        conda_env = context.obj.get('conda_env')
        kwargs = dict(executable=context.obj.get('mip_exe'), email=email,
                      conda_env=conda_env)
        restart_api.restart(script_dir, config_path, **kwargs)

        if case:
            new_entry = build_pending(most_recent.case_id,
                                      most_recent.root_dir,
                                      most_recent.type)
            commit_analysis(context.obj['manager'], new_entry)
