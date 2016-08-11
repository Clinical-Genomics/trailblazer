# -*- coding: utf-8 -*-
from datetime import date
import logging

import click
from path import path

from . import api

log = logging.getLogger(__name__)


@click.command()
@click.argument('case_id')
@click.pass_context
def delete(context, case_id):
    """Delete an analysis and files."""
    manager = context.obj['manager']
    analysis_obj = api.analyses(analysis_id=case_id).one()
    if analysis_obj.is_deleted:
        click.echo("this analysis is already deleted")
    else:
        click.echo("you are about to delete: {}".format(analysis_obj.root_dir))
        if click.confirm('are you sure?'):
            path(analysis_obj.root_dir).rmtree_p()
            analysis_obj.is_deleted = True
            manager.commit()
            click.echo("removed: {}".format(analysis_obj.root_dir))


@click.command('list')
@click.option('-p', '--pretty', is_flag=True)
@click.option('-l', '--limit', default=10)
@click.option('-s', '--since', nargs=3, type=int)
@click.option('-c', '--config', is_flag=True)
@click.argument('analysis_id', required=False)
@click.pass_context
def list_cmd(context, pretty, limit, since, config, analysis_id):
    """List added analyses."""
    if since:
        since = date(*since)
    query = (api.analyses(analysis_id=analysis_id, since=since,
                          is_ready=config)
                .limit(limit))

    if query.first() is None:
        log.warn('sorry, no analyses found')
    else:
        if config:
            paths = (analysis.config_path for analysis in query)
            click.echo(' '.join(paths))
        else:
            for analysis in query:
                click.echo(analysis.to_json(pretty=pretty))
