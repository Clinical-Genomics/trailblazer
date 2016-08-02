# -*- coding: utf-8 -*-
import logging

import click

from analysis.store import get_manager

log = logging.getLogger(__name__)


@click.command()
@click.option('-d', '--database')
@click.option('-r', '--reset', is_flag=True)
@click.pass_context
def init(context, database, reset):
    """Setup the analysis package."""
    db_uri = database or context.obj['database']
    log.info("setup a new database: %s", db_uri)
    db = get_manager(db_uri)
    if reset:
        db.drop_all()
    db.create_all()
