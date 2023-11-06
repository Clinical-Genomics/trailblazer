"""Store backend in Trailblazer."""
import datetime as dt
import logging
from typing import Callable, Dict, List, Optional, Union

import alchy
import sqlalchemy as sqa
from alchy import Query

from trailblazer.constants import TrailblazerStatus
from trailblazer.store.core import CoreHandler
from trailblazer.store.filters.analyses_filters import (
    AnalysisFilter,
    apply_analysis_filter,
)
from trailblazer.store.models import Analysis, Model

LOG = logging.getLogger(__name__)


class BaseHandler(CoreHandler):
    Analysis = Analysis

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
        #
        return analyses.order_by(self.Analysis.started_at.desc())

    def analyses(
        self,
        case_id: str = None,
        query: str = None,
        status: str = None,
        deleted: bool = None,
        temp: bool = False,
        before: dt.datetime = None,
        is_visible: bool = None,
        family: str = None,
        data_analysis: str = None,
        comment: str = None,
    ) -> Query:
        """
        used by REST +> CG
        Fetch analyses from the database."""
        if not case_id:
            case_id = family

        analysis_query = self.Analysis.query
        if case_id:
            analysis_query = analysis_query.filter_by(family=case_id)
        if query:  # to be deprecated
            analysis_query = analysis_query.filter(
                sqa.or_(
                    self.Analysis.family.ilike(f"%{query}%"),
                    self.Analysis.status.ilike(f"%{query}%"),
                    self.Analysis.data_analysis.ilike(f"%{query}%"),
                    self.Analysis.comment.ilike(f"%{query}%"),
                )
            )
        if status:
            analysis_query = analysis_query.filter_by(status=status)
        if isinstance(deleted, bool):
            analysis_query = analysis_query.filter_by(is_deleted=deleted)
        if temp:
            analysis_query = analysis_query.filter(
                self.Analysis.status.in_(TrailblazerStatus.ongoing_statuses())
            )
        if before:
            analysis_query = analysis_query.filter(self.Analysis.started_at < before)
        if is_visible is not None:
            analysis_query = analysis_query.filter_by(is_visible=is_visible)
        if data_analysis:
            analysis_query = analysis_query.filter(
                Analysis.data_analysis.ilike(f"%{data_analysis}%")
            )
        if comment:
            analysis_query = analysis_query.filter(Analysis.comment.ilike(f"%{comment}%"))

        return analysis_query.order_by(self.Analysis.started_at.desc())


class Store(alchy.Manager, BaseHandler):
    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
