from sqlalchemy.orm import Query

from trailblazer.store.crud.create import CreateHandler
from trailblazer.store.crud.delete import DeleteHandler
from trailblazer.store.crud.read import ReadHandler
from trailblazer.store.crud.update import UpdateHandler


class Store(
    CreateHandler,
    DeleteHandler,
    ReadHandler,
    UpdateHandler,
):
    """Aggregating class for the store API handlers."""

    def paginate_query(self, query: Query, page: int, per_page: int) -> Query:
        return query.limit(per_page).offset((page - 1) * per_page)
