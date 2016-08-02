# -*- coding: utf-8 -*-
from datetime import datetime
import logging

import click
from path import path
import yaml

from analysis.store import Analysis, get_manager
from analysis import utils

log = logging.getLogger(__name__)


def build_analysis(qcsampleinfo):
    """Build database record from analysis output."""
    data = yaml.load(qcsampleinfo)
    fam_key = data.keys()[0]
    fam_data = data[fam_key][fam_key]
    started_at = fam_data['AnalysisDate']
    famanalysis_out = path(fam_data['Program']['QCCollect']['OutDirectory'])
    customer = fam_data['InstanceTag'][0]
    values = {
        'name': "{}-{}".format(customer, fam_key),
        'pipeline': 'mip',
        'pipeline_version': data[fam_key][fam_key]['MIPVersion'],
        'type': data[fam_key][fam_key]['AnalysisType'],
        'root_dir': famanalysis_out.parent.parent,
        'started_at': fam_data['AnalysisDate'],
    }

    if fam_data['AnalysisRunStatus'] == 'Finished':
        values['status'] = 'completed'
    else:
        sacct_out = utils.get_sacctout(famanalysis_out)
        if sacct_out is None:
            if (datetime.now() - started_at).days > 2:
                values['status'] = 'errored'
                values['failed_step'] = 'time'
            else:
                # expect the analysis is already running
                values['status'] = 'running'
        else:
            with open(sacct_out, 'r') as stream:
                error_jobs = utils.inspect_error(stream)
            if len(error_jobs) > 0:
                values['status'] = 'errored'
                values['failed_step'] = error_jobs[0]['name']
            else:
                # not sure what's going on...
                raise ValueError(famanalysis_out)
    return Analysis(**values)


@click.command('add')
@click.argument('qcsampleinfo', type=click.File('r'))
@click.pass_context
def add_cmd(context, qcsampleinfo):
    """Add an analysis to the database."""
    manager = get_manager(context.obj['database'])
    new_analysis = build_analysis(qcsampleinfo)
    old_analysis = Analysis.query.filter_by(name=new_analysis.name)
    if old_analysis:
        log.debug("deleting existing analysis: %s", new_analysis.name)
        old_analysis.delete()
    manager.add_commit(new_analysis)
    log.info("added new analysis: %s", new_analysis.name)
