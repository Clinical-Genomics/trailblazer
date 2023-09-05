import os

from flask_alchy import Alchy

from trailblazer.store.api import BaseHandler
from trailblazer.store.models import Model

ANALYSIS_HOST = os.environ.get("ANALYSIS_HOST")


class TrailblazerAlchy(Alchy, BaseHandler):
    pass


store = TrailblazerAlchy(Model=Model)
