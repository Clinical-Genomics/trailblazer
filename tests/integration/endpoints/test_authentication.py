from http import HTTPStatus

from flask import g
from flask.testing import FlaskClient

from trailblazer.dto import CreateJobRequest
from trailblazer.store.models import Analysis
from trailblazer.store.store import Store

TYPE_JSON = "application/json"


def test_add_job_to_analysis(client: FlaskClient, analysis: Analysis, store: Store, flask_app):
    # GIVEN an endpoint decorated with before_request
    # GIVEN that both X-On-Behalf-Of and Authorization are set as headers
    with flask_app.test_request_context(
        "/analysis/1/jobs",
        headers={"X-On-Behalf-Of": "Bearer eyhgi2", "Authorization": "Bearer eyeeyeeye"},
    ):
        # WHEN calling before_request upon calling the endpoint
        flask_app.preprocess_request()

        # THEN the user is set using the On-Behalf-Of header
        assert g.current_user
