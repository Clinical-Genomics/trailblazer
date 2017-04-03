# -*- coding: utf-8 -*-
import logging

import click
from path import Path

from trailblazer.add import add_cmd
from trailblazer.store import api

log = logging.getLogger(__name__)


@click.command()
@click.argument('cust_dirs', type=click.Path(exists=True), nargs=-1,
                help='customer root directories')
@click.pass_context
def scan(context, cust_dirs):
    """Scan directories for analyses."""
    for cust_dir in cust_dirs:
        log.debug("scanning customer dir: %s", cust_dir)
        sampleinfo_files = scan_dir(cust_dir)
        for sampleinfo in sampleinfo_files:
            log.debug("adding analysis: %s", sampleinfo)
            with open(sampleinfo, 'r') as stream:
                context.invoke(add_cmd, qcsampleinfo=stream)

    api.track_update()
    context.obj['manager'].commit()


def scan_dir(root_dir):
    """Scan root for MIP analyses.

    Will look for qc sample info files.
    """
    mip4_files = Path(root_dir).glob('*/analysis/*_qc_sample_info.yaml')
    return mip4_files
