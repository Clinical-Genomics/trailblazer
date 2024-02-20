import os
from http import HTTPStatus
from typing import Mapping

from flask import (
    Blueprint,
    Response,
    abort,
    g,
    jsonify,
    make_response,
    request,
)
from google.auth import jwt
from pydantic import ValidationError
from dependency_injector.wiring import inject, Provide

from trailblazer.containers import Container
from trailblazer.dto import (
    AnalysesRequest,
    AnalysesResponse,
    AnalysisResponse,
    AnalysisUpdateRequest,
    CreateJobRequest,
    JobResponse,
    FailedJobsRequest,
    FailedJobsResponse,
)
from trailblazer.dto.analyses_response import UpdateAnalysesResponse
from trailblazer.dto.create_analysis_request import CreateAnalysisRequest
from trailblazer.dto.update_analyses import UpdateAnalyses
from trailblazer.exc import MissingAnalysis
from trailblazer.server.ext import store
from trailblazer.server.utils import (
    parse_analyses_request,
    parse_analysis_update_request,
    parse_get_failed_jobs_request,
    parse_job_create_request,
    stringify_timestamps,
)
from trailblazer.services.analysis_service import AnalysisService
from trailblazer.services.job_service import JobService
from trailblazer.store.models import Info

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")


@blueprint.before_request
def before_request():
    """Authentication that is run before processing requests to the application"""
    if request.method == "OPTIONS":
        return make_response(jsonify(ok=True), 204)
    if os.environ.get("SCOPE") == "DEVELOPMENT":
        return
    if auth_header := request.headers.get("Authorization"):
        jwt_token = auth_header.split("Bearer ")[-1]
    else:
        return abort(403, "no JWT token found on request")

    user_data: Mapping = jwt.decode(jwt_token, verify=False)
    if user := store.get_user(email=user_data["email"], exclude_archived=True):
        g.current_user = user
    else:
        return abort(403, f"{user_data['email']} doesn't have access")


@blueprint.route("/analyses", methods=["GET"])
@inject
def get_analyses(analysis_service: AnalysisService = Provide[Container.analysis_service]):
    try:
        request_data: AnalysesRequest = parse_analyses_request(request)
        response: AnalysesResponse = analysis_service.get_analyses(request_data)
        return jsonify(response.model_dump()), HTTPStatus.OK
    except ValidationError as error:
        return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


@blueprint.route("/analyses", methods=["PATCH"])
@inject
def patch_analyses(analysis_service: AnalysisService = Provide[Container.analysis_service]):
    """Update data (such as status, visibility, comments etc.) for multiple analyses at once."""
    try:
        request_data = UpdateAnalyses.model_validate(request.json)
        response: UpdateAnalysesResponse = analysis_service.update_analyses(request_data)
        return jsonify(response.model_dump()), HTTPStatus.OK
    except ValidationError as error:
        return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST
    except MissingAnalysis as error:
        return jsonify(error=str(error)), HTTPStatus.NOT_FOUND


@blueprint.route("/analyses/<int:analysis_id>", methods=["GET"])
@inject
def get_analysis(
    analysis_id: int, analysis_service: AnalysisService = Provide[Container.analysis_service]
):
    try:
        response: AnalysisResponse = analysis_service.get_analysis(analysis_id)
        return jsonify(response.model_dump()), HTTPStatus.OK
    except MissingAnalysis as error:
        return jsonify(error=str(error)), HTTPStatus.NOT_FOUND


@blueprint.route("/analysis/<int:analysis_id>/jobs", methods=["POST"])
@inject
def add_job(analysis_id: int, job_service: JobService = Provide[Container.job_service]):
    try:
        job_request: CreateJobRequest = parse_job_create_request(request)
        response: JobResponse = job_service.add_job(analysis_id=analysis_id, data=job_request)
        return jsonify(response.model_dump()), HTTPStatus.CREATED
    except MissingAnalysis as error:
        return jsonify(error=str(error)), HTTPStatus.NOT_FOUND
    except ValidationError as error:
        return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


@blueprint.route("/analyses/<int:analysis_id>", methods=["PUT"])
@inject
def update_analysis(
    analysis_id: int, analysis_service: AnalysisService = Provide[Container.analysis_service]
):
    try:
        request_data: AnalysisUpdateRequest = parse_analysis_update_request(request)
        response: AnalysisResponse = analysis_service.update_analysis(
            analysis_id=analysis_id, update=request_data
        )
        return jsonify(response.model_dump()), HTTPStatus.OK
    except MissingAnalysis as error:
        return jsonify(error=str(error)), HTTPStatus.NOT_FOUND
    except ValidationError as error:
        return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


@blueprint.route("/info")
def info():
    """Display metadata about database."""
    info: Info = store.get_query(table=Info).first()
    return jsonify(**info.to_dict())


@blueprint.route("/me")
def me():
    """Return information about a logged in user."""
    return jsonify(**g.current_user.to_dict())


@blueprint.route("/aggregate/jobs", methods=["GET"])
@inject
def get_failed_jobs(job_service: JobService = Provide[Container.job_service]):
    try:
        query: FailedJobsRequest = parse_get_failed_jobs_request(request)
        response: FailedJobsResponse = job_service.get_failed_jobs(query)
        return jsonify(response.model_dump()), HTTPStatus.OK
    except ValidationError as error:
        return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


# CG REST INTERFACE ###
# ONLY POST routes which accept messages in specific format
# NOT for use with GUI (for now)


@blueprint.route("/get-latest-analysis", methods=["POST"])
def post_get_latest_analysis():
    """Return latest analysis entry for specified case id."""
    post_request = request.json
    case_id: str = post_request.get("case_id")
    if latest_case_analysis := store.get_latest_analysis_for_case(case_id):
        raw_analysis: dict[str, str] = stringify_timestamps(latest_case_analysis.to_dict())
        return jsonify(**raw_analysis), HTTPStatus.OK
    return jsonify(None), HTTPStatus.OK


@blueprint.route("/add-pending-analysis", methods=["POST"])
@inject
def post_add_pending_analysis(
    analysis_service: AnalysisService = Provide[Container.analysis_service],
):
    try:
        request_data = CreateAnalysisRequest.model_validate(request.json)
        response: AnalysisResponse = analysis_service.add_pending_analysis(request_data)
        return jsonify(response.model_dump()), HTTPStatus.CREATED
    except ValidationError as error:
        return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


@blueprint.route("/set-analysis-uploaded", methods=["PUT"])
def set_analysis_uploaded():
    """Set the analysis uploaded at attribute."""
    put_request: Response.json = request.json
    try:
        store.update_analysis_uploaded_at(
            case_id=put_request.get("case_id"), uploaded_at=put_request.get("uploaded_at")
        )
        return jsonify("Success! Uploaded at request sent"), HTTPStatus.CREATED
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT


@blueprint.route("/set-analysis-status", methods=["PUT"])
def set_analysis_status():
    """Update analysis status of a case with supplied status."""
    put_request: Response.json = request.json
    try:
        case_id: str = put_request.get("case_id")
        status: str = put_request.get("status")
        store.update_analysis_status(case_id=case_id, status=status)
        return (
            jsonify(f"Success! Analysis set to {put_request.get('status')} request sent"),
            HTTPStatus.CREATED,
        )
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT


@blueprint.route("/add-comment", methods=["PUT"])
def add_comment():
    """Updating comment on analysis."""
    put_request: Response.json = request.json
    try:
        case_id: str = put_request.get("case_id")
        comment: str = put_request.get("comment")
        store.update_analysis_comment(case_id=case_id, comment=comment)
        return jsonify("Success! Adding comment request sent"), HTTPStatus.CREATED
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT
