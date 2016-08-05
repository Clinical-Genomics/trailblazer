# -*- coding: utf-8 -*-
from datetime import datetime
import logging

import click
from path import path
import yaml

from analysis.store import Analysis
from analysis import utils
from analysis.exc import MissingFileError, UnknownError

log = logging.getLogger(__name__)


def build_analysis(data):
    """Build database record from analysis output.

    Is the analysis running or errored?
    - 0. Can we find a Sacct output?
        - no: was it started > 24 hours ago?
            - yes: error/time
            - no: running
        - yes: do we find errors in the log?
            - yes: are the time points after start of analysis?
                - yes: error/[reason]
                - no: running
            - no: uhm, no idea ;)
    """
    fam_key = data.keys()[0]
    fam_data = data[fam_key][fam_key]
    sample_ids = data[fam_key].keys()
    sample_ids.remove(fam_key)
    analysis_start = fam_data['AnalysisDate']
    analysis_type = data[fam_key][fam_key]['AnalysisType']
    analysis_out = path(fam_data['Program']['QCCollect']['OutDirectory'])
    customer = fam_data['InstanceTag'][0]
    case_id = "{}-{}".format(customer, fam_key)
    config_path = analysis_out.parent.joinpath(analysis_type, fam_key,
                                               "{}_config.yaml".format(fam_key))
    values = {
        'case_id': case_id,
        'pipeline': 'mip',
        'pipeline_version': data[fam_key][fam_key]['MIPVersion'],
        'type': analysis_type,
        'root_dir': analysis_out.parent.parent,
        'started_at': analysis_start,
        'config_path': config_path,
    }

    if fam_data['AnalysisRunStatus'] in ('Finished', 'Archived', 'Archiving'):
        values['status'] = 'completed'
    else:
        sacct_out = utils.get_sacctout(analysis_out)
        long_since_start = (datetime.now() - analysis_start).seconds > 86400
        if sacct_out is None:
            if long_since_start:
                # if the analysis should've finished but hasn't
                # pending possible errors
                values['status'] = 'failed'
                values['failed_step'] = 'time'
            else:
                # assume the analysis is still running without fails
                values['status'] = 'running'
        else:
            with open(sacct_out, 'r') as stream:
                error_jobs = utils.inspect_error(stream)
            if len(error_jobs) > 0:
                first_fail = error_jobs[0]
                if analysis_start > first_fail['start']:
                    # the analysis has been restarted
                    # the Sacct errors don't belong to this analysis!
                    if long_since_start:
                        values['status'] = 'failed'
                        values['failed_step'] = 'time'
                    else:
                        values['status'] = 'running'
                else:
                    values['status'] = 'failed'
                    values['failed_step'] = first_fail['name']
                    values['failed_at'] = first_fail['start']
            else:
                # the status in QC sample info should be "Finished"...
                raise UnknownError(case_id)

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
    manager = context.obj['manager']
    data = yaml.load(qcsampleinfo)
    family_id = data.keys()[0]
    if is_newest(data):
        try:
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
                    log.debug("deleting existing analysis: %s",
                              new_analysis.case_id)
                    old_analysis.delete()
                    manager.commit()
                manager.add_commit(new_analysis)
                log.info("added new analysis: %s - %s", new_analysis.case_id,
                         new_analysis.status)
        except MissingFileError:
            log.error("missing status file for: %s", family_id)
    else:
        log.debug("analysis version not supported: %s", family_id)
