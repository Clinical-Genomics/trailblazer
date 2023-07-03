from sqlalchemy.orm import Query
from dataclasses import dataclass
from typing import Type

from trailblazer.store.models import Model, Job
import sqlalchemy as sqa


@dataclass
class BaseHandler_2:
    """All models in one base class."""

    def __init__(self):
        pass

    def get_query(self, table: Type[Model]) -> Query:
        """Return a query for the given table."""
        return self.query(table)

    def get_job_query_with_name_and_count_labels(self) -> Query:
        """Return a Job query with a name label and a counter with a label."""
        return self.session.query(
            Job.name.label("name"),
            sqa.func.count(Job.id).label("count"),
        )
