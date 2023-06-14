from alchy import Query
from dataclasses import dataclass
from typing import Type

from trailblazer.store.models import Model


@dataclass
class BaseHandler_2:
    """All models in one base class."""

    def __init__(self):
        pass

    def get_query(self, table: Type[Model]) -> Query:
        """Return a query for the given table."""
        return self.query(table)
