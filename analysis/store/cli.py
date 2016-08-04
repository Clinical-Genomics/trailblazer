# -*- coding: utf-8 -*-
from datetime import date
import logging

import click
from path import path

from .models import Analysis

log = logging.getLogger(__name__)


def delete_analysis(manager, case_id, started_at):
    """Delete an analysis."""
    analysis_obj = (Analysis.query
                            .filter_by(case_id=case_id, started_at=started_at)
                            .one())
    analysis_obj.delete()
    manager.commit()


@click.command()
@click.argument('case_id')
@click.pass_context
def delete(context, case_id):
    """Delete an analysis and files."""
    manager = context.obj['manager']
    analysis_obj = Analysis.query.filter_by(case_id=case_id).one()
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
    query = Analysis.query.order_by(Analysis.started_at)

    if since:
        since_date = date(*since)
        log.debug("filter analyses on date: %s", since_date)
        query = query.filter(Analysis.started_at > since_date)

    if analysis_id:
        log.debug("filter analyses on id pattern: %s", analysis_id)
        query = query.filter(Analysis.case_id.contains(analysis_id))

    if query.first() is None:
        log.warn('sorry, no analyses found')
    else:
        if config:
            query = query.filter_by(status='completed', is_deleted=False)
            paths = (analysis.config_path for analysis in query)
            click.echo(' '.join(paths))
        else:
            for analysis in query.limit(limit):
                click.echo(analysis.to_json(pretty=pretty))
