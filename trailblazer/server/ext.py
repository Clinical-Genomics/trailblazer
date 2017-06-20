# -*- coding: utf-8 -*-
from flask_alchy import Alchy

from trailblazer.store import BaseHandler, models


class TrailblazerAlchy(Alchy, BaseHandler):
    pass


store = TrailblazerAlchy(Model=models.Model)
