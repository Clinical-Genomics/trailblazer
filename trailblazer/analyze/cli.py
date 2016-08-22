# -*- coding: utf-8 -*-
import click

from .restart import update_maxgaussian
from .start import start_mip


@click.group()
@click.pass_context
def analyze(context):
    pass


@analyze.command()
@click.option('-p', '--ccp', type=click.Path(exists=True), required=True)
@click.option('-a', '--analysis-type', default='genomes')
@click.option('-f', '--family', required=True)
@click.option('-c', '--config', type=click.Path(exists=True))
@click.option('-x', '--executable', type=click.Path(exists=True))
@click.option('-i', '--customer')
@click.option('-g', '--gene-list')
@click.option('--dryrun', is_flag=True)
@click.option('-o', '--out', type=click.File('w'), default='-')
@click.option('-e', '--conda-env')
@click.pass_context
def start(context, ccp, analysis_type, family, config, customer, gene_list,
          dryrun, executable, out, conda_env):
    """Start a new analysis."""
    config = config or context.obj['mip_config']
    executable = executable or context.obj['mip_exe']
    gene_list = gene_list or context.obj['mip_genelist']
    conda_env = conda_env or context.obj.get('conda_env')

    script = start_mip(
        analysis_type,
        family,
        config,
        ccp,
        executable=executable,
        customer=customer,
        gene_list=gene_list,
        dryrun=dryrun,
        conda_env=conda_env)

    click.echo(script, file=out)


@analyze.group()
@click.pass_context
def restart(context):
    pass


@restart.command('max-gaussian')
@click.argument('config_path', type=click.Path(exists=True))
@click.pass_context
def max_gaussian(context, config_path):
    """Update config file to restart with Max Gaussian for SNV enabled."""
    update_maxgaussian(config_path)
    click.echo("updated: {}".format(config_path))
