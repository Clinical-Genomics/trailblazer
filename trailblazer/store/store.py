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
