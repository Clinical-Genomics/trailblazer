from trailblazer.store.crud.read import ReadHandler
from trailblazer.store.crud.update import UpdateHandler


class CoreHandler(
    UpdateHandler,
    ReadHandler,
):
    """Aggregating class for the store API handlers."""

    def __init__(self):
        pass
