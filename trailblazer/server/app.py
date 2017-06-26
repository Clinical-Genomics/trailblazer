# -*- coding: utf-8 -*-
import os

import coloredlogs
from flask import Flask
from flask_cors import CORS

from trailblazer.server import api, ext

coloredlogs.install(level='INFO')
app = Flask(__name__)

SECRET_KEY = 'unsafe!!!'
TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_POOL_RECYCLE = 7200
SQLALCHEMY_TRACK_MODIFICATIONS = 'FLASK_DEBUG' in os.environ

app.config.from_object(__name__)

# register blueprints
app.register_blueprint(api.blueprint)

# configure extensions
ext.store.init_app(app)
cors = CORS(app, resources={r"/api/*": {'origins': '*'}})


@app.route('/')
def index():
    return "Welcome to Trailblazer REST API"
