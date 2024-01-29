import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_reverse_proxy import FlaskReverseProxied
from sqlalchemy.orm import scoped_session
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient

from trailblazer.server import api, ext
from trailblazer.server.wiring import setup_dependency_injection
from trailblazer.services.analysis_service import AnalysisService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.store.database import get_session
from trailblazer.store.store import Store

app = Flask(__name__)
setup_dependency_injection()

LOG = logging.getLogger(__name__)

# Environment variables
SECRET_KEY = "unsafe!!!"
TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
SQLALCHEMY_POOL_RECYCLE = os.environ.get("SQLALCHEMY_POOL_RECYCLE", 7200)
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("FLASK_DEBUG", False)
ANALYSIS_HOST: str = os.environ.get("ANALYSIS_HOST")

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
