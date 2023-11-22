import datetime
import multiprocessing
import os
from http import HTTPStatus
from typing import Mapping

from flask import Blueprint, Response, abort, g, jsonify, make_response, request
from google.auth import jwt
from sqlalchemy.orm import Query

from trailblazer.constants import (
    ONE_MONTH_IN_DAYS,
    TRAILBLAZER_TIME_STAMP,
    TrailblazerStatus,
)
from trailblazer.server.ext import store
from trailblazer.store.models import Analysis, Info, User
from trailblazer.utils.datetime import get_date_number_of_days_ago

ANALYSIS_HOST: str = os.environ.get("ANALYSIS_HOST")

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")


def stringify_timestamps(data: dict) -> dict[str, str]:
    """Convert datetime into string before dumping in order to avoid information loss"""
    for key, val in data.items():
        if isinstance(val, datetime.datetime):
            data[key] = str(val)
    return data


@blueprint.before_request
def before_request():
    """Authentication that is run before processing requests to the application"""
    if request.method == "OPTIONS":
        return make_response(jsonify(ok=True), 204)
    if os.environ.get("SCOPE") == "DEVELOPMENT":
        return
    auth_header = request.headers.get("Authorization")
    if auth_header:
        jwt_token = auth_header.split("Bearer ")[-1]
    else:
        return abort(403, "no JWT token found on request")

    user_data: Mapping = jwt.decode(jwt_token, verify=False)
    user: User = store.get_user(email=user_data["email"], exclude_archived=True)
    if not user:
        return abort(403, f"{user_data['email']} doesn't have access")
    g.current_user = user


@blueprint.route("/analyses")
def analyses():
    """Display analyses."""
    per_page = int(request.args.get("per_page", 100))
    page = int(request.args.get("page", 1))
    analyses: Query = store.get_analyses_query_by_search_term_and_is_visible(
        search_term=request.args.get("query"),
        is_visible=bool(request.args.get("is_visible")),
    )

    query_page: Query = store.paginate_query(query=analyses, page=page, per_page=per_page)
    response_data = []
    for analysis in query_page.all():
        analysis_data = analysis.to_dict()
        analysis_data["user"] = analysis.user.to_dict() if analysis.user else None
        response_data.append(analysis_data)
    return jsonify(analyses=response_data)


@blueprint.route("/analyses/<int:analysis_id>", methods=["GET", "PUT"])
def analysis(analysis_id):
    """Retrieve or update an analysis."""
    analysis: Analysis = store.get_analysis_with_id(analysis_id)
    if analysis is None:
        return abort(404)

    if request.method == "PUT":
        status: str | None = request.json.get("status")
        comment: str | None = request.json.get("comment")
        is_visible: bool | None = request.json.get("is_visible")
        store.update_analysis(
            analysis_id=analysis_id, comment=comment, status=status, is_visible=is_visible
        )

    data = analysis.to_dict()
    data["jobs"] = [job.to_dict() for job in analysis.jobs]
    data["user"] = analysis.user.to_dict() if analysis.user else None
    return jsonify(**data)


@blueprint.route("/info")
def info():
    """Display metadata about database."""
    info: Info = store.get_query(table=Info).first()
    return jsonify(**info.to_dict())


@blueprint.route("/me")
def me():
    """Return information about a logged in user."""
    return jsonify(**g.current_user.to_dict())


@blueprint.route("/aggregate/jobs")
def aggregate_jobs():
    """Return stats about failed jobs."""
    time_window: datetime = get_date_number_of_days_ago(
        number_of_days_ago=int(request.args.get("days_back", ONE_MONTH_IN_DAYS))
    )
    failed_jobs: list[dict[str, str | int]] = store.get_nr_jobs_with_status_per_category(
        status=TrailblazerStatus.FAILED, since_when=time_window
    )
    return jsonify(jobs=failed_jobs)


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
def update_analysis(analysis_id):
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
    post_request: Response.json = request.json
    latest_case_analysis: Analysis | None = store.get_latest_analysis_for_case(
        case_id=post_request.get("case_id")
    )
    if latest_case_analysis:
        raw_analysis: dict[str, str] = stringify_timestamps(latest_case_analysis.to_dict())
        return jsonify(**raw_analysis), HTTPStatus.OK
    return jsonify(None), HTTPStatus.OK


@blueprint.route("/find-analysis", methods=["POST"])
def post_find_analysis():
    """Find analysis using case id, date, and status."""
    post_request: Response.json = request.json
    analysis: Analysis = store.get_analysis(
        case_id=post_request.get("case_id"),
        started_at=datetime.strptime(post_request.get("started_at"), TRAILBLAZER_TIME_STAMP).date(),
        status=post_request.get("status"),
    )
    if analysis:
        raw_analysis: dict[str, str] = stringify_timestamps(analysis.to_dict())
        return jsonify(**raw_analysis), HTTPStatus.OK
    return jsonify(None), HTTPStatus.OK


@blueprint.route("/delete-analysis", methods=["POST"])
def post_delete_analysis():
    """Delete analysis using analysis_id. If analysis is ongoing, an error will be raised.
    To delete ongoing analysis, --force flag should also be passed.
    If an ongoing analysis is deleted in ths manner, all ongoing jobs will be cancelled"""
    post_request: Response.json = request.json
    try:
        store.delete_analysis(
            analysis_id=post_request.get("analysis_id"), force=post_request.get("force")
        )
        return jsonify(None), HTTPStatus.CREATED
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT


@blueprint.route("/mark-analyses-deleted", methods=["POST"])
def post_mark_analyses_deleted():
    """Mark all analysis belonging to a case as deleted."""
    post_request: Response.json = request.json
    case_analyses: list[Analysis] | None = store.update_case_analyses_as_deleted(
        case_id=post_request.get("case_id")
    )
    raw_analysis = [
        stringify_timestamps(case_analysis.to_dict()) for case_analysis in case_analyses
    ]
    if raw_analysis:
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
        store.update_analysis_status(
            case_id=put_request.get("case_id"), status=put_request.get("status")
        )
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
        store.update_analysis_comment(
            case_id=put_request.get("case_id"), comment=put_request.get("comment")
        )
        return jsonify("Success! Adding comment request sent"), HTTPStatus.CREATED
    except Exception as error:
        return jsonify(f"Exception: {error}"), HTTPStatus.CONFLICT
