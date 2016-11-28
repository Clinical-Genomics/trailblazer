# -*- coding: utf-8 -*-
import logging

import click
import yaml
from sqlalchemy.exc import IntegrityError

from trailblazer.exc import MissingFileError
from .commit import commit_analysis
from .core import build_entry
from .utils import is_latest_mip

log = logging.getLogger(__name__)


@click.command('add')
@click.option('-s', '--sacct', type=click.File('r'))
@click.argument('qcsampleinfo', type=click.File('r'))
@click.pass_context
def add_cmd(context, sacct, qcsampleinfo):
    """Add an analysis to the database."""
    manager = context.obj['manager']
    sampleinfo_data = yaml.load(qcsampleinfo)
    if is_latest_mip(sampleinfo_data):
        try:
            new_entry = build_entry(sampleinfo_data, sacct_stream=sacct)
            log.debug("entry: %s - %s", new_entry.case_id, new_entry.status)
            with open(new_entry.config_path, 'r') as in_handle:
                config_data = yaml.load(in_handle)
                email = config_data.get('email')
            commit_analysis(manager, new_entry, email=email)
        except MissingFileError as error:
            log.error("missing file: %s", error.message)
        except IntegrityError as error:
            log.exception(error.message)
            manager.session.rollback()
    else:
        family_id = sampleinfo_data.keys()[0]
        log.debug("analysis version not supported: %s", family_id)
