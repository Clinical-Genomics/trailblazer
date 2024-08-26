import os
from http import HTTPStatus
from typing import Mapping

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, Response, abort, g, jsonify, make_response, request
from google.auth import jwt

from trailblazer.containers import Container
from trailblazer.dto import (
    AnalysesRequest,
    AnalysesResponse,
    AnalysisResponse,
    AnalysisUpdateRequest,
    CreateJobRequest,
    FailedJobsRequest,
    FailedJobsResponse,
    JobResponse,
)
from trailblazer.dto.analyses_response import UpdateAnalysesResponse
from trailblazer.dto.authentication.code_exchange_request import CodeExchangeRequest
from trailblazer.dto.create_analysis_request import CreateAnalysisRequest
from trailblazer.dto.summaries_request import SummariesRequest
from trailblazer.dto.summaries_response import SummariesResponse
from trailblazer.dto.update_analyses import UpdateAnalyses
from trailblazer.server.ext import store
from trailblazer.server.utils import (
    handle_endpoint_errors,
    parse_analyses_request,
    stringify_timestamps,
)
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.authentication_service.authentication_service import AuthenticationService
from trailblazer.services.job_service import JobService
from trailblazer.store.models import Info, User

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")


@blueprint.before_request
def before_request():
    """Authentication that is run before processing requests to the application"""
    if request.endpoint == "api.authenticate":
        return
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


@blueprint.route("/auth", methods=["POST"])
@handle_endpoint_errors
@inject
def authenticate(auth_service: AuthenticationService = Provide[Container.auth_service]):
    """Exchange authorization code for an access token."""
    request_data = CodeExchangeRequest.model_validate(request.json)
    token: str = auth_service.authenticate(request_data.code)
    return jsonify({"token": token}), HTTPStatus.OK


@blueprint.route("/auth/refresh", methods=["GET"])
@handle_endpoint_errors
@inject
def refresh_token(auth_service: AuthenticationService = Provide[Container.auth_service]):
    """Refresh access token."""
    user: User = g.current_user
    token: str = auth_service.refresh_token(user.id)
    return jsonify({"token": token}), HTTPStatus.OK


@blueprint.route("/analyses", methods=["GET"])
@handle_endpoint_errors
@inject
def get_analyses(analysis_service: AnalysisService = Provide[Container.analysis_service]):
    request_data: AnalysesRequest = parse_analyses_request(request)
    response: AnalysesResponse = analysis_service.get_analyses(request_data)
    return jsonify(response.model_dump()), HTTPStatus.OK


@blueprint.route("/analyses", methods=["PATCH"])
@handle_endpoint_errors
@inject
def patch_analyses(analysis_service: AnalysisService = Provide[Container.analysis_service]):
    """Update data (such as status, visibility, comments etc.) for multiple analyses at once."""
    request_data = UpdateAnalyses.model_validate(request.json)
    user: User = g.get("current_user")
    response: UpdateAnalysesResponse = analysis_service.update_analyses(
        data=request_data, user=user
    )
    return jsonify(response.model_dump()), HTTPStatus.OK


@blueprint.route("/analyses/<int:analysis_id>", methods=["GET"])
@handle_endpoint_errors
@inject
def get_analysis(
    analysis_id: int,
    analysis_service: AnalysisService = Provide[Container.analysis_service],
):
    response: AnalysisResponse = analysis_service.get_analysis(analysis_id)
    return jsonify(response.model_dump()), HTTPStatus.OK


@blueprint.route("/analyses/<int:analysis_id>/cancel", methods=["POST"])
@handle_endpoint_errors
@inject
def cancel_analysis(
    analysis_id: int,
    analysis_service: AnalysisService = Provide[Container.analysis_service],
):
    response: AnalysisResponse = analysis_service.cancel_analysis_from_web(analysis_id)
    return jsonify(response.model_dump()), HTTPStatus.OK


@blueprint.route("/analysis/<int:analysis_id>/jobs", methods=["POST"])
@handle_endpoint_errors
@inject
def add_job(analysis_id: int, job_service: JobService = Provide[Container.job_service]):
    data = CreateJobRequest.model_validate(request.json)
    response: JobResponse = job_service.add_job(analysis_id=analysis_id, data=data)
    return jsonify(response.model_dump()), HTTPStatus.CREATED


@blueprint.route("/analyses/<int:analysis_id>", methods=["PUT"])
@handle_endpoint_errors
@inject
def update_analysis(
    analysis_id: int, analysis_service: AnalysisService = Provide[Container.analysis_service]
):
    request_data = AnalysisUpdateRequest.model_validate(request.json)
    user: User = g.get("current_user")
    response: AnalysisResponse = analysis_service.update_analysis(
        analysis_id=analysis_id, update=request_data, user=user
    )
    return jsonify(response.model_dump()), HTTPStatus.OK


@blueprint.route("/summary", methods=["GET"])
@handle_endpoint_errors
@inject
def get_summaries(analysis_service: AnalysisService = Provide[Container.analysis_service]):
    request_data = SummariesRequest.model_validate(request.args)
    response: SummariesResponse = analysis_service.get_summaries(request_data)
    return jsonify(response.model_dump()), HTTPStatus.OK


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
@handle_endpoint_errors
@inject
def get_failed_jobs(job_service: JobService = Provide[Container.job_service]):
    request_data = FailedJobsRequest.model_validate(request.args)
    response: FailedJobsResponse = job_service.get_failed_jobs(request_data)
    return jsonify(response.model_dump()), HTTPStatus.OK


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
@handle_endpoint_errors
@inject
def add_pending_analysis(analysis_service: AnalysisService = Provide[Container.analysis_service]):
    request_data = CreateAnalysisRequest.model_validate(request.json)
    response: AnalysisResponse = analysis_service.add_pending_analysis(request_data)
    return jsonify(response.model_dump()), HTTPStatus.CREATED


@blueprint.route("/set-analysis-uploaded", methods=["PUT"])
@handle_endpoint_errors
def set_analysis_uploaded():
    """Set the analysis uploaded at attribute."""
    put_request: Response.json = request.json
    store.update_analysis_uploaded_at(
        case_id=put_request.get("case_id"), uploaded_at=put_request.get("uploaded_at")
    )
    return jsonify("Success! Uploaded at request sent"), HTTPStatus.CREATED


@blueprint.route("/set-analysis-status", methods=["PUT"])
@handle_endpoint_errors
def set_analysis_status():
    """Update analysis status of a case with supplied status."""
    put_request: Response.json = request.json
    case_id: str = put_request.get("case_id")
    status: str = put_request.get("status")
    store.update_analysis_status_by_case_id(case_id=case_id, status=status)
    return (
        jsonify(f"Success! Analysis set to {put_request.get('status')} request sent"),
        HTTPStatus.CREATED,
    )


@blueprint.route("/add-comment", methods=["PUT"])
@handle_endpoint_errors
def add_comment():
    """Updating comment on analysis."""
    put_request: Response.json = request.json
    case_id: str = put_request.get("case_id")
    comment: str = put_request.get("comment")
    store.update_latest_analysis_comment(case_id=case_id, comment=comment)
    return jsonify("Success! Adding comment request sent"), HTTPStatus.CREATED
