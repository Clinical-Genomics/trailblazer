# -*- coding: utf-8 -*-
from datetime import date
import logging

import click
from path import path

from . import api

log = logging.getLogger(__name__)


@click.command()
@click.option('-p', '--pending', is_flag=True, help='remove pending runs only')
@click.argument('case_id')
@click.pass_context
def delete(context, pending, case_id):
    """Delete an analysis and files."""
    manager = context.obj['manager']
    analysis_runs = api.analyses(analysis_id=case_id)
    for analysis_obj in analysis_runs:
        if pending:
            if analysis_obj.status == 'pending':
                click.echo("removing: {}".format(analysis_obj.id))
                analysis_obj.delete()
                manager.commit()
        else:
            if analysis_obj.is_deleted:
                click.echo("this analysis is already deleted")
            else:
                click.echo("you are about to delete: {}"
                           .format(analysis_obj.root_dir))
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
@click.option('-o', '--older', is_flag=True)
@click.option('-d', '--complete', is_flag=True, help='check if complete')
@click.argument('analysis_id', required=False)
@click.pass_context
def list_cmd(context, pretty, limit, since, older, config, complete,
             analysis_id):
    """List added analyses."""
    if since:
        since = date(*since)
    query = (api.analyses(analysis_id=analysis_id, since=since,
                          is_ready=config, older=older)
                .limit(limit))

    if query.first() is None:
        log.warn('sorry, no analyses found')
    else:
        if analysis_id and complete:
            # return the earliest date for a completed run
            query = query.filter_by(status='completed')
            if query.count() == 0:
                log.error("case not analyzed successfully")
                context.abort()
            else:
                dates = sorted(analysis.completed_at for analysis in query)
                click.echo(dates[0])
        if config:
            paths = (analysis.config_path for analysis in query)
            click.echo(' '.join(paths))
        else:
            for analysis in query:
                click.echo(analysis.to_json(pretty=pretty))
