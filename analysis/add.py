# -*- coding: utf-8 -*-
import logging

import click
from path import path
import yaml

from analysis.store import Analysis, get_manager
from analysis import utils

log = logging.getLogger(__name__)


def build_analysis(data):
    """Build database record from analysis output."""
    fam_key = data.keys()[0]
    fam_data = data[fam_key][fam_key]
    sample_ids = data[fam_key].keys()
    sample_ids.remove(fam_key)
    started_at = fam_data['AnalysisDate']
    famanalysis_out = path(fam_data['Program']['QCCollect']['OutDirectory'])
    customer = fam_data['InstanceTag'][0]
    values = {
        'case_id': "{}-{}".format(customer, fam_key),
        'pipeline': 'mip',
        'pipeline_version': data[fam_key][fam_key]['MIPVersion'],
        'type': data[fam_key][fam_key]['AnalysisType'],
        'root_dir': famanalysis_out.parent.parent,
        'started_at': started_at,
    }

    if fam_data['AnalysisRunStatus'] == 'Finished':
        values['status'] = 'completed'
    else:
        sacct_out = "{}.status".format(fam_data['lastLogFilePath'])
        with open(sacct_out, 'r') as stream:
            error_jobs = utils.inspect_error(stream)
        if len(error_jobs) > 0:
            values['status'] = 'errored'
            values['failed_step'] = error_jobs[0]['name']
            values['failed_at'] = error_jobs[0]['start']
        else:
            # assume the analysis is still running without fails
            values['status'] = 'running'

    new_analysis = Analysis(**values)
    new_analysis.samples = sample_ids
    return new_analysis


def is_newest(data):
    """Check if the analysis is up to date."""
    fam_key = data.keys()[0]
    version = data[fam_key][fam_key].get('MIPVersion')
    return version is not None and version.startswith('v3.')


def is_updated(old_analysis, new_analysis):
    """Check if a new analysis has been updated."""
    return any((old_analysis.status != new_analysis.status,
                old_analysis.failed_step != new_analysis.failed_step,
                old_analysis.failed_at != new_analysis.failed_at))


@click.command('add')
@click.argument('qcsampleinfo', type=click.File('r'))
@click.pass_context
def add_cmd(context, qcsampleinfo):
    """Add an analysis to the database."""
    manager = get_manager(context.obj['database'])
    data = yaml.load(qcsampleinfo)
    if is_newest(data):
        new_analysis = build_analysis(data)
        filters = dict(case_id=new_analysis.case_id,
                       started_at=new_analysis.started_at)
        old_analysis = (Analysis.query.filter_by(**filters)
                                      .order_by(Analysis.started_at.desc())
                                      .first())
        if old_analysis and not is_updated(old_analysis, new_analysis):
            log.debug("nothing updated since last analysis: %s",
                      new_analysis.case_id)
        else:
            if old_analysis and old_analysis.status == 'running':
                # replace if status was 'running'
                log.debug("deleting existing analysis: %s", new_analysis.case_id)
                old_analysis.delete()
                manager.commit()
            manager.add_commit(new_analysis)
            log.info("added new analysis: %s", new_analysis.case_id)
    else:
        log.warn("analysis version not supported: %s", data.keys()[0])
