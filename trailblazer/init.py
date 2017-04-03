# -*- coding: utf-8 -*-
import logging

import click

from trailblazer.store import api, Metadata

log = logging.getLogger(__name__)


@click.command()
@click.option('-d', '--database', help='SQLAlchemy database connection string')
@click.option('-r', '--reset', is_flag=True, help='delete existing tables before setup')
@click.pass_context
def init(context, database, reset):
    """Setup the analysis package."""
    db_uri = database or context.obj['database']
    log.info("setup a new database: %s", uri_secure(db_uri))
    manager = api.connect(db_uri)
    if reset:
        manager.drop_all()
    manager.create_all()
    # add inital metadata record (for web interface)
    new_metadata = Metadata()
    manager.add_commit(new_metadata)


def uri_secure(uri_str):
    """Convert URI to replace sensitive information with stars."""
    pass_end = uri_str.find('@')
    if pass_end != -1:
        pass_start = uri_str.rfind(':', 0, pass_end)
        secure_uri = uri_str[:pass_start] + ':' + '*****' + uri_str[pass_end:]
        return secure_uri
    else:
        return uri_str
