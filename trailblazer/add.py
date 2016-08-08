# -*- coding: utf-8 -*-
from datetime import datetime
import logging

import click
from path import path
import yaml

from trailblazer.store import Analysis
from trailblazer import utils
from trailblazer.exc import MissingFileError, UnknownError

log = logging.getLogger(__name__)


def parse_sampleinfo(sampleinfo):
    """Extract basic info from loaded sampleinfo file.

    Args:
        sampleinfo (dict): loaded contents from sampleinfo file
    """
    fam_key = sampleinfo.keys()[0]
    fam_data = sampleinfo[fam_key][fam_key]
    sample_ids = sampleinfo[fam_key].keys()
    sample_ids.remove(fam_key)
    analysis_start = fam_data['AnalysisDate']
    analysis_type = fam_data['AnalysisType']
    analysis_out = path(fam_data['Program']['QCCollect']['OutDirectory'])
    customer = fam_data['InstanceTag'][0]
    case_id = "{}-{}".format(customer, fam_key)
    cluster_const = analysis_out.parent.parent.parent
    config_path = cluster_const.joinpath(analysis_type, fam_key,
                                         "{}_config.yaml".format(fam_key))
    values = {
        'case_id': case_id,
        'pipeline': 'mip',
        'pipeline_version': fam_data['MIPVersion'],
        'type': analysis_type,
        'root_dir': analysis_out.parent.parent,
        'started_at': analysis_start,
        'config_path': config_path,
        'samples': sample_ids,
        'analysis_status': fam_data['AnalysisRunStatus'],
    }
    return values


def parse_status(analysis_status, analysis_start, sacct_out=None):
    """Parse the status for a MIP analysis."""
    if analysis_status in ('Finished', 'Archived', 'Archiving'):
        return dict(status='completed')
    else:
        # analysis status is "notFinished" - find out why!
        long_since_start = (datetime.now() - analysis_start).seconds > 86400
        if sacct_out is None:
            # we can't really tell if something went wrong
            if long_since_start:
                # if the analysis should've finished but hasn't
                return dict(status='failed', failed_step='time')
            else:
                # assume the analysis is still running without fails
                return dict(status='running')
        else:
            error_jobs = utils.inspect_error(sacct_out)
            if len(error_jobs) > 0:
                # we found some failed jobs!
                first_fail = error_jobs[0]
                if analysis_start > first_fail['start']:
                    # the analysis has been restarted
                    # the Sacct errors don't belong to this analysis!
                    if long_since_start:
                        # long since start, still not completed
                        return dict(status='failed', failed_step='time')
                    else:
                        return dict(status='running')
                else:
                    # Sacct output belongs to this analysis
                    return dict(status='failed',
                                failed_step=first_fail['name'],
                                failed_at=first_fail['start'])
            else:
                # the status in QC sample info should be "Finished"...
                raise UnknownError()


def build_analysis(sampleinfo):
    """Build database record from analysis output."""
    values = parse_sampleinfo(sampleinfo)
    sacct_out = utils.get_sacctout(values['root_dir'])
    args = dict(analysis_status=values['analysis_status'],
                analysis_start=values['started_at'])
    if sacct_out:
        with open(sacct_out) as stream:
            status = parse_status(sacct_out=stream, **args)
    else:
        status = parse_status(**args)

    values.update(status)
    del values['analysis_status']
    new_analysis = Analysis(**values)
    new_analysis.samples = values['samples']
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
