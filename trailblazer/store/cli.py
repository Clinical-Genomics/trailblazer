# -*- coding: utf-8 -*-
from datetime import date, timedelta
import logging

import click
from path import Path

from . import api

log = logging.getLogger(__name__)


@click.command()
@click.option('-p', '--pending', is_flag=True, help='remove pending runs only')
@click.option('-y', '--yes', is_flag=True, help='automate check')
@click.option('-f', '--force', is_flag=True)
@click.option('-l', '--limit', default=10, help='limit number of runs')
@click.argument('case_id', required=False)
@click.pass_context
def delete(context, pending, yes, force, limit, case_id):
    """Delete an analysis and files."""
    manager = context.obj['manager']
    if case_id:
        analysis_runs = api.analyses(analysis_id=case_id)
    else:
        # check all analyses more than 2 weeks old
        two_weeks_ago = date.today() - timedelta(days=14)
        analysis_runs = api.analyses(since=two_weeks_ago, older=True,
                                     deleted=False)

    for analysis_obj in analysis_runs.limit(limit):
        log.info("working on case: %s", analysis_obj.case_id)
        if pending:
            if analysis_obj.status == 'pending':
                click.echo("removing: {}".format(analysis_obj.id))
                analysis_obj.delete()
                manager.commit()
        else:
            # check that no more recent analysis exists
            more_recent = api.analyses(analysis_obj.case_id).first()
            not_most_recent = (more_recent and
                               more_recent.logged_at > analysis_obj.logged_at)
            if not_most_recent:
                log.warn("more recent run exists: %s", more_recent.logged_at)
                if not force:
                    continue

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
                          is_ready=config, older=older))

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
        else:
            query = query.limit(limit)
            if config:
                paths = (analysis.config_path for analysis in query)
                click.echo(' '.join(paths))
            else:
                for analysis in query:
                    click.echo(analysis.to_json(pretty=pretty))
