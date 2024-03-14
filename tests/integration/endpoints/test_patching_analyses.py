from http import HTTPStatus

from flask.testing import FlaskClient

from trailblazer.dto.update_analyses import AnalysisUpdate, UpdateAnalyses
from trailblazer.store.models import Analysis


def test_patch_analysis(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis

    # GIVEN a valid request to pach the analysis
    update = AnalysisUpdate(id=analysis.id, comment="new_comment")
    request = UpdateAnalyses(analyses=[update])
    data: str = request.model_dump_json()

    # WHEN patching the analysis
    response = client.patch("/api/v1/analyses", data=data, content_type="application/json")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return the analysis
    assert response.json["analyses"]
