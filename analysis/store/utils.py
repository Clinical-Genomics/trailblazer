# -*- coding: utf-8 -*-
import logging

from alchy import Manager

from .models import Model

log = logging.getLogger(__name__)


def get_manager(uri):
    log.debug('open connection to database: %s', uri)
    db = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return db
