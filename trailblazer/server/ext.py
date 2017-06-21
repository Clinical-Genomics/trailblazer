# -*- coding: utf-8 -*-
from flask_alchy import Alchy

from trailblazer.server.auth import AuthManager
from trailblazer.store import BaseHandler, models


class TrailblazerAlchy(Alchy, BaseHandler):
    pass


store = TrailblazerAlchy(Model=models.Model)
auth = AuthManager(store)
