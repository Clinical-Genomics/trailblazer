# -*- coding: utf-8 -*-
import logging

import click
from path import path

from .models import Analysis
from .utils import get_manager

log = logging.getLogger(__name__)


def delete_analysis(manager, name):
    """Delete an analysis."""
    analysis_obj = Analysis.query.filter_by(name=name).one()
    analysis_obj.delete()
    manager.commit()


@click.command()
@click.argument('name')
@click.pass_context
def delete(context, name):
    """Delete an analysis and files."""
    manager = get_manager(context.obj['database'])
    analysis_obj = Analysis.query.filter_by(name=name).one()
    click.echo("you are about to delete: {}".format(analysis_obj.root_dir))
    if click.confirm('are you sure?'):
        path(analysis_obj.root_dir).rmtree_p()
        analysis_obj.delete()
        manager.commit()
        click.echo("removed: {}".format(analysis_obj.root_dir))


@click.command('list')
@click.option('-c', '--compressed', is_flag=True)
@click.option('-l', '--limit', default=10)
@click.argument('analysis_id', required=False)
@click.pass_context
def list_cmd(context, analysis_id, compressed, limit):
    """List added analyses."""
    get_manager(context.obj['database'])
    query = Analysis.query.order_by(Analysis.started_at)

    if analysis_id:
        log.debug("filter analyses on id pattern: ", analysis_id)
        query = query.filter(Analysis.name.contains(analysis_id))

    if query.first() is None:
        log.warn('sorry, no analyses found')
    else:
        for analysis in query.limit(limit):
            click.echo(analysis.to_json(pretty=not compressed))
