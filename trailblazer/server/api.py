import datetime
import multiprocessing
import os
from http import HTTPStatus
from typing import Mapping

from flask import Blueprint, Response, abort, current_app, g, jsonify, make_response, request
from google.auth import jwt
from pydantic import ValidationError

from trailblazer.constants import (
    TRAILBLAZER_TIME_STAMP,
)

from trailblazer.dto import (
    AnalysesRequest,
    AnalysisResponse,
    AnalysesResponse,
    AnalysisUpdateRequest,
    FailedJobsRequest,
    FailedJobsResponse,
)
from trailblazer.exc import MissingAnalysis
from trailblazer.server.ext import store
from trailblazer.server.utils import (
    parse_analyses_request,
    parse_analysis_update_request,
    parse_get_failed_jobs_request,
    stringify_timestamps,
)
from trailblazer.services import AnalysisService, JobService
from trailblazer.store.models import Analysis, Info

ANALYSIS_HOST: str = os.environ.get("ANALYSIS_HOST")

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
def get_analyses():
    analysis_service: AnalysisService = current_app.extensions.get("analysis_service")
    try:
        query: AnalysesRequest = parse_analyses_request(request)
        response: AnalysesResponse = analysis_service.get_analyses(query)
        return jsonify(response.model_dump()), HTTPStatus.OK
    except ValidationError as error:
        return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


@blueprint.route("/analyses/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    analysis_service: AnalysisService = current_app.extensions.get("analysis_service")
    try:
        response: AnalysisResponse = analysis_service.get_analysis(analysis_id)
        return jsonify(response.model_dump()), HTTPStatus.OK
    except MissingAnalysis as error:
        return jsonify(error=str(error)), HTTPStatus.NOT_FOUND


@blueprint.route("/analyses/<int:analysis_id>", methods=["PUT"])
def update_analysis(analysis_id):
    analysis_service: AnalysisService = current_app.extensions.get("analysis_service")
    try:
        update: AnalysisUpdateRequest = parse_analysis_update_request(request)
        response: AnalysisResponse = analysis_service.update_analysis(
            analysis_id=analysis_id, update=update
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
def get_failed_jobs():
    job_service: JobService = current_app.extensions.get("job_service")
    try:
        query: FailedJobsRequest = parse_get_failed_jobs_request(request)
        response: FailedJobsResponse = job_service.get_failed_jobs(query)
        return jsonify(response.model_dump()), HTTPStatus.OK
    except ValidationError as error:
        return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST


@blueprint.route("/update-all")
def update_analyses():
    """Update all ongoing analysis by querying SLURM."""
    process = multiprocessing.Process(
        target=store.update_ongoing_analyses,
        kwargs={"analysis_host": ANALYSIS_HOST},
    )
    process.start()
    return jsonify(f"Success! Trailblazer updated {datetime.datetime.now()}"), HTTPStatus.CREATED


@blueprint.route("/update/<int:analysis_id>", methods=["PUT"])
def update_analysis_via_process(analysis_id):
    """Update a specific analysis."""
    try:
        process = multiprocessing.Process(
            target=store.update_run_status,
            kwargs={"analysis_id": analysis_id, "analysis_host": ANALYSIS_HOST},
        )
        process.start()
        return jsonify("Success! Update request sent"), HTTPStatus.CREATED
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT


@blueprint.route("/cancel/<int:analysis_id>", methods=["PUT"])
def cancel(analysis_id):
    """Cancel an analysis and all slurm jobs associated with it."""
    auth_header = request.headers.get("Authorization")
    jwt_token = auth_header.split("Bearer ")[-1]
    user_data = jwt.decode(jwt_token, verify=False)
    try:
        process = multiprocessing.Process(
            target=store.cancel_ongoing_analysis,
            kwargs={
                "analysis_id": analysis_id,
                "analysis_host": ANALYSIS_HOST,
                "email": user_data["email"],
            },
        )
        process.start()
        return jsonify("Success! Cancel request sent"), HTTPStatus.CREATED
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT


@blueprint.route("/delete/<int:analysis_id>", methods=["PUT"])
def delete(analysis_id):
    """Delete an analysis and all slurm jobs associated with it."""
    try:
        process = multiprocessing.Process(
            target=store.delete_analysis,
            kwargs={"analysis_id": analysis_id, "force": True},
        )
        process.start()
        return jsonify("Success! Delete request sent!"), HTTPStatus.CREATED
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT


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


@blueprint.route("/find-analysis", methods=["POST"])
def post_find_analysis():
    """Find analysis using case id, date, and status."""
    post_request: Response.json = request.json
    case_id: str = post_request.get("case_id")
    started_at = datetime.strptime(post_request.get("started_at"), TRAILBLAZER_TIME_STAMP).date()
    status: str = post_request.get("status")
    if analysis := store.get_analysis(
        case_id=case_id,
        started_at=started_at,
        status=status,
    ):
        raw_analysis: dict[str, str] = stringify_timestamps(analysis.to_dict())
        return jsonify(**raw_analysis), HTTPStatus.OK
    return jsonify(None), HTTPStatus.OK


@blueprint.route("/delete-analysis", methods=["POST"])
def post_delete_analysis():
    """Delete analysis using analysis_id. If analysis is ongoing, an error will be raised.
    To delete ongoing analysis, --force flag should also be passed.
    If an ongoing analysis is deleted in ths manner, all ongoing jobs will be cancelled"""
    post_request: Response.json = request.json
    analysis_id: str = post_request.get("analysis_id")
    force: str = post_request.get("force")
    try:
        store.delete_analysis(analysis_id=analysis_id, force=force)
        return jsonify(None), HTTPStatus.CREATED
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT


@blueprint.route("/mark-analyses-deleted", methods=["POST"])
def post_mark_analyses_deleted():
    """Mark all analysis belonging to a case as deleted."""
    post_request: Response.json = request.json
    case_id: str = post_request.get("case_id")
    case_analyses: list[Analysis] | None = store.update_case_analyses_as_deleted(case_id)
    if raw_analysis := [
        stringify_timestamps(case_analysis.to_dict()) for case_analysis in case_analyses
    ]:
        return jsonify(*raw_analysis), HTTPStatus.CREATED
    return jsonify(None), HTTPStatus.CREATED


@blueprint.route("/add-pending-analysis", methods=["POST"])
def post_add_pending_analysis():
    """Add new analysis with status: pending."""
    post_request: Response.json = request.json
    try:
        analysis: Analysis = store.add_pending_analysis(
            case_id=post_request.get("case_id"),
            email=post_request.get("email"),
            type=post_request.get("type"),
            config_path=post_request.get("config_path"),
            out_dir=post_request.get("out_dir"),
            priority=post_request.get("priority"),
            data_analysis=post_request.get("data_analysis"),
            ticket_id=post_request.get("ticket"),
            workflow_manager=post_request.get("workflow_manager"),
        )
        raw_analysis: dict = stringify_timestamps(analysis.to_dict())
        return jsonify(**raw_analysis), 201
    except Exception as exception:
        return jsonify(f"Exception: {exception}"), 409


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
