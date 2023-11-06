"""Store backend in Trailblazer."""
import logging
from typing import Callable, Dict, List, Optional, Union

import alchy
from alchy import Query

from trailblazer.store.core import CoreHandler
from trailblazer.store.filters.analyses_filters import (
    AnalysisFilter,
    apply_analysis_filter,
)
from trailblazer.store.models import Analysis, Model

LOG = logging.getLogger(__name__)


class BaseHandler(CoreHandler):
    def setup(self):
        self.create_all()



class Store(alchy.Manager, BaseHandler):
    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
