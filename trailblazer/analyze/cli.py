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
@click.option('--ccp', type=click.Path(exists=True))
@click.option('-c', '--config', type=click.Path(exists=True))
@click.option('-x', '--executable', type=click.Path(exists=True))
@click.option('-g', '--gene-list')
@click.option('-e', '--email', help='email to send errors to')
@click.option('-p', '--priority', type=click.Choice(['low', 'normal', 'high']),
              default='normal')
@click.option('--dryrun', is_flag=True)
@click.argument('customer')
@click.argument('family')
@click.pass_context
def start(context, ccp, config, executable, gene_list, email, priority, dryrun,
          customer, family):
    """Start a new analysis."""
    ccp_abs = (Path(ccp).abspath() if ccp else
               Path(context.obj['analysis_root']).joinpath(customer))
    # parse pedigree yaml
    pedigree_path = ccp_abs.joinpath("{0}/{0}_pedigree.yaml".format(family))
    if not pedigree_path.exists():
        log.error("pedigree YAML doesn't exist")
        context.abort()

    # check if case is already running
    case_id = "{}-{}".format(customer, family)
    if api.is_running(case_id):
        log.error("case already running!")
        context.abort()

    global_config = config or context.obj['mip_config']
    executable = executable or context.obj['mip_exe']
    gene_list = gene_list or context.obj.get('mip_genelist')
    email = email or environ_email()

    process = start_mip(
        config=global_config,
        family_id=family,
        ccp=ccp_abs,
        executable=executable,
        gene_list=gene_list,
        dryrun=dryrun,
        email=email,
        priority=priority,
    )
    process.wait()
    if process.returncode != 0:
        log.error("error starting analysis, check the output")
        context.abort()

    # add pending entry to database
    new_entry = build_pending(case_id, ccp_abs)
    if email:
        user = api.user(email)
        new_entry.user = user
    commit_analysis(context.obj['manager'], new_entry)
    context.obj['manager'].commit()


@analyze.command()
@click.option('--max-gaussian', is_flag=True)
@click.option('-d', '--disable', type=click.Choice(BRANCH_OPTIONS),
              multiple=True)
@click.option('-s', '--start-from', type=click.Choice(restart_api.PROGRAMS))
@click.option('-e', '--extras', multiple=True, type=(str, str))
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
        kwargs = dict(executable=context.obj['mip_exe'], email=email)
        process = start_mip(config=config_path, **kwargs)
        process.wait()
        if process.returncode != 0:
            log.error("error starting analysis, check the output")
            context.abort()

        if case:
            new_entry = build_pending(most_recent.case_id,
                                      most_recent.root_dir)
            commit_analysis(context.obj['manager'], new_entry)


def environ_email():
    """Guess email from sudo user environment variable."""
    username = os.environ.get('SUDO_USER')
    if username:
        return "{}@scilifelab.se".format(username)
