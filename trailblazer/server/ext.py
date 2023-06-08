from flask_alchy import Alchy

from trailblazer.store.api import BaseHandler
from trailblazer.store import models


class TrailblazerAlchy(Alchy, BaseHandler):
    pass


store = TrailblazerAlchy(Model=models.Model)
