import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_reverse_proxy import FlaskReverseProxied
from sqlalchemy.orm import scoped_session

from trailblazer.server import api, ext
from trailblazer.store.database import get_session

app = Flask(__name__)

LOG = logging.getLogger(__name__)

SECRET_KEY = "unsafe!!!"
TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
SQLALCHEMY_POOL_RECYCLE = os.environ.get("SQLALCHEMY_POOL_RECYCLE", 7200)
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("FLASK_DEBUG", False)

app.config.from_object(__name__)

# register blueprints
app.register_blueprint(api.blueprint)

# configure extensions
FlaskReverseProxied(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
ext.store.init_app(app)


@app.route("/")
def index():
    return "Welcome to Trailblazer REST API"


@app.teardown_appcontext
def teardown_session(_):
    """
    Remove the database session to ensure database resources are released when a
    request has been processed.
    """
    session: scoped_session = get_session()
    session.remove()
