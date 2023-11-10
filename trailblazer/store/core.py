import alchy

from trailblazer.store.crud.create import CreateHandler
from trailblazer.store.crud.delete import DeleteHandler
from trailblazer.store.crud.read import ReadHandler
from trailblazer.store.crud.update import UpdateHandler
from trailblazer.store.models import Model


class CoreHandler(
    CreateHandler,
    DeleteHandler,
    ReadHandler,
    UpdateHandler,
):
    """Aggregating class for the store API handlers."""

    def __init__(self):
        pass


class Store(alchy.Manager, CoreHandler):
    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
