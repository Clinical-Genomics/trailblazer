from flask_alchy import Alchy

from trailblazer.store.api import BaseHandler
from trailblazer.store.models import Model


class TrailblazerAlchy(Alchy, BaseHandler):
    pass


store = TrailblazerAlchy(Model=Model)
