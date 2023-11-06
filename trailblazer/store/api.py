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

    def get_analyses_query_by_search_term_and_is_visible(
        self,
        search_term: Optional[str] = None,
        is_visible: bool = False,
    ) -> Query:
        """Return analyses by searchb term qnd is visible."""
        if not search_term and not is_visible:
            return
        filter_map: Dict[Callable, Optional[Union[str, bool]]] = {
            AnalysisFilter.FILTER_BY_IS_VISIBLE: is_visible,
            AnalysisFilter.FILTER_BY_SEARCH_TERM: search_term,
        }
        filter_functions: List[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        analyses: Query = apply_analysis_filter(
            filter_functions=filter_functions,
            analyses=self.get_query(table=Analysis),
            search_term=search_term,
        )
        return analyses.order_by(Analysis.started_at.desc())


class Store(alchy.Manager, BaseHandler):
    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
