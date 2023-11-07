"""Store backend in Trailblazer."""
import logging

import alchy

from trailblazer.store.core import CoreHandler
from trailblazer.store.models import Model

LOG = logging.getLogger(__name__)


class BaseHandler(CoreHandler):
    def setup(self):
        self.create_all()


class Store(alchy.Manager, BaseHandler):
    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
