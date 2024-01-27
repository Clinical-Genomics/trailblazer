import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_reverse_proxy import FlaskReverseProxied
from sqlalchemy.orm import scoped_session
from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmApiClient
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient

from trailblazer.server import api, ext
from trailblazer.services.analysis_service import AnalysisService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.store.database import get_session
from trailblazer.store.store import Store

app = Flask(__name__)

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

# Clients
slurm_cli_client = SlurmCLIClient(ANALYSIS_HOST)
store = Store()

# Services
slurm_service = SlurmCLIService(slurm_cli_client)
analysis_service = AnalysisService(store)
job_service = JobService(store=store, slurm_service=slurm_service)

# configure extensions
FlaskReverseProxied(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
ext.store.init_app(app)

# Register services (we should use dependency injection instead. See dependency-injector for example.)
app.extensions["analysis_service"] = analysis_service
app.extensions["job_service"] = job_service


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
