# -*- coding: utf-8 -*-
import logging

import click

from trailblazer.add import add_cmd
from trailblazer import utils

log = logging.getLogger(__name__)


@click.command()
@click.argument('cust_dirs', type=click.Path(exists=True), nargs=-1)
@click.pass_context
def scan(context, cust_dirs):
    """Scan directory(ies) for analyses."""
    for cust_dir in cust_dirs:
        log.debug("scanning customer dir: %s", cust_dir)
        sampleinfo_files = utils.scan(cust_dir)
        for sampleinfo in sampleinfo_files:
            log.debug("adding analysis: %s", sampleinfo)
            with open(sampleinfo, 'r') as stream:
                context.invoke(add_cmd, qcsampleinfo=stream)
