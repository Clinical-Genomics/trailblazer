# -*- coding: utf-8 -*-
import logging

import click
from dateutil.parser import parse as parse_date
from path import Path
import yaml

from . import api
from .models import STATUS_OPTIONS

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
    statuses = ['running', 'pending'] if pending else 'completed'
    analysis_runs = api.analyses(analysis_id=case_id, status=statuses)
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
                continue
            elif analysis_obj.config_path is None:
                click.echo("ERROR - missing analysis information! ({})"
                           .format(analysis_obj.case_id))
                continue
            else:
                analysis_root_path = Path(analysis_obj.root_dir)
                if not analysis_root_path.exists():
                    # the analysis is already deleted
                    click.echo("analysis already deleted: {}"
                               .format(analysis_obj.case_id))
                    for analysis_obj in api.analyses(analysis_id=case_id):
                        analysis_obj.is_deleted = True
                    manager.commit()
                    continue
                elif (not analysis_root_path.endswith('analysis') or
                      (analysis_obj.config_path not in analysis_root_path.listdir())):
                    click.echo("ERROR - review analysis output path: ({})"
                               .format(analysis_root_path))
                    continue

                # make sure this is the current analysis on disk
                qcsample_path = analysis_obj.config_path.replace('_config.yaml',
                                                                 '_qc_sample_info.yaml')
                with open(qcsample_path, 'r') as handle:
                    qcsample_data = yaml.load(handle)
                if qcsample_data['analysis_date'] != analysis_obj.started_at:
                    click.echo("analysis record doesn't match current run")
                    continue

                click.echo("you are about to delete: {}"
                           .format(analysis_obj.root_dir))
                if yes or click.confirm('are you sure?'):
                    analysis_root_path.rmtree_p()
                    # MIP only stores the latest analysis
                    # if one is deleted - they all should count as deleted!
                    for analysis_obj in api.analyses(analysis_id=case_id):
                        analysis_obj.is_deleted = True
                    manager.commit()
                    click.echo("removed: {}".format(analysis_obj.root_dir))


@click.command('list')
@click.option('--condensed', is_flag=True, help='condense output')
@click.option('-l', '--limit', default=10)
@click.option('-s', '--since', help='return analysis since a date')
@click.option('-d', '--deleted/--no-deleted', is_flag=True)
@click.option('-d', '--display', type=click.Choice(['json', 'id', 'config', 'count']),
              default='json')
@click.option('-o', '--older', is_flag=True)
@click.option('-p', '--complete', is_flag=True, help='check if complete')
@click.option('-v', '--version', help='filter on pipeline version')
@click.option('-t', '--status', type=click.Choice(STATUS_OPTIONS))
@click.argument('case_id', required=False)
@click.pass_context
def list_cmd(context, condensed, limit, since, older, display, complete,
             deleted, case_id, version, status):
    """List added runs."""
    if since:
        since = parse_date(since)
    query = api.analyses(analysis_id=case_id, since=since, older=older,
                         is_ready=(True if display == 'config' else False),
                         deleted=(None if deleted is None else deleted),
                         version=version, status=status)
    if display == 'count':
        log.info("number of runs: %s", query.count())
    elif query.first() is None:
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
