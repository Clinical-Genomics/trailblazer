# -*- coding: utf-8 -*-
import logging

import click
from dateutil.parser import parse as parse_date
from path import Path

from . import api

log = logging.getLogger(__name__)


@click.command()
@click.option('-p', '--pending', is_flag=True, help='remove pending runs only')
@click.option('-y', '--yes', is_flag=True, help='automate check')
@click.option('-f', '--force', is_flag=True)
@click.option('-l', '--latest', is_flag=True, help='only delete latest run')
@click.argument('case_id')
@click.pass_context
def delete(context, pending, yes, force, latest, case_id):
    """Delete an analysis and files."""
    manager = context.obj['manager']
    analysis_runs = api.analyses(analysis_id=case_id)
    if latest and analysis_runs.first():
        analysis_runs = [analysis_runs.first()]

    for analysis_obj in analysis_runs:
        log.debug("working on case: %s", analysis_obj.case_id)
        if pending:
            if analysis_obj.status in ('pending', 'running'):
                click.echo("removing: {}".format(analysis_obj.id))
                analysis_obj.delete()
                manager.commit()
        else:
            if analysis_obj.is_deleted:
                click.echo("this analysis is already deleted")
            else:
                click.echo("you are about to delete: {}"
                           .format(analysis_obj.root_dir))
                if yes or click.confirm('are you sure?'):
                    Path(analysis_obj.root_dir).rmtree_p()
                    analysis_obj.is_deleted = True
                    manager.commit()
                    click.echo("removed: {}".format(analysis_obj.root_dir))


@click.command('list')
@click.option('--condensed', is_flag=True, help='condense output')
@click.option('-l', '--limit', default=10)
@click.option('-s', '--since', help='return analysis since a date')
@click.option('-d', '--deleted/--no-deleted', is_flag=True)
@click.option('-d', '--display', type=click.Choice(['json', 'id', 'config']),
              default='json')
@click.option('-o', '--older', is_flag=True)
@click.option('-p', '--complete', is_flag=True, help='check if complete')
@click.argument('case_id', required=False)
@click.pass_context
def list_cmd(context, condensed, limit, since, older, display, complete,
             deleted, case_id):
    """List added runs."""
    if since:
        since = parse_date(since)
    query = api.analyses(analysis_id=case_id, since=since, older=older,
                         is_ready=(True if display == 'config' else False),
                         deleted=(None if deleted is None else deleted))
    if query.first() is None:
        log.warn('sorry, no analyses found')
    else:
        if case_id and complete:
            # return the earliest date for a completed run
            query = query.filter_by(status='completed')
            if query.count() == 0:
                log.error("case not analyzed successfully")
                context.abort()
            else:
                dates = sorted(analysis.completed_at for analysis in query)
                click.echo(dates[0])
        else:
            for analysis in query.limit(limit):
                if display == 'config':
                    click.echo(analysis.config_path)
                elif display == 'id':
                    click.echo(analysis.case_id)
                else:
                    click.echo(analysis.to_json(pretty=(not condensed)))
