from flask_alchy import Alchy

from trailblazer.store.core import CoreHandler
from trailblazer.store.models import Model


class TrailblazerAlchy(Alchy, CoreHandler):
    pass


store = TrailblazerAlchy(Model=Model)
