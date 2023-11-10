import os
from typing import Optional

from flask import Flask
from flask_cors import CORS
from flask_reverse_proxy import FlaskReverseProxied
from sqlalchemy.orm import scoped_session

from trailblazer.server import api, ext
from trailblazer.store.database import get_scoped_session_registry, get_session, initialize_database

app = Flask(__name__)

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
ext.store.init_app(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Initialize database
initialize_database(app.config["SQLALCHEMY_DATABASE_URI"])


@app.route("/")
def index():
    return "Welcome to Trailblazer REST API"


@app.teardown_appcontext
def teardown_session():
    """
    Remove the database session to ensure database resources are released when a
    request has been processed.
    """
    registry: Optional[scoped_session] = get_scoped_session_registry()
    if registry:
        registry.remove()
