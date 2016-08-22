# -*- coding: utf-8 -*-
import click

from .restart import update_maxgaussian


@click.group()
@click.pass_context
def analyze(context):
    pass


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
