import datetime
import multiprocessing
import os
from typing import Dict, Mapping

from dateutil.parser import parse as parse_datestr
from flask import Blueprint, abort, g, jsonify, make_response, request, Response
from google.auth import jwt

from trailblazer.server.ext import store

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")


def stringify_timestamps(data: dict) -> Dict[str, str]:
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
    user_obj = store.user(user_data["email"], include_archived=False)
    if user_obj is None:
        return abort(403, f"{user_data['email']} doesn't have access")
    g.current_user = user_obj


@blueprint.route("/analyses")
def analyses():
    """Display analyses."""
    per_page = int(request.args.get("per_page", 100))
    page = int(request.args.get("page", 1))
    query = store.analyses(
        status=request.args.get("status"),
        query=request.args.get("query"),
        is_visible=request.args.get("is_visible") == "true" or None,
    )

    query_page = query.paginate(page, per_page=per_page)
    data = []
    for analysis_obj in query_page.items:
        analysis_data = analysis_obj.to_dict()
        analysis_data["user"] = analysis_obj.user.to_dict() if analysis_obj.user else None
        analysis_data["failed_jobs"] = [job_obj.to_dict() for job_obj in analysis_obj.failed_jobs]
        data.append(analysis_data)

    return jsonify(analyses=data)


@blueprint.route("/analyses/<int:analysis_id>", methods=["GET", "PUT"])
def analysis(analysis_id):
    """Display a single analysis."""
    analysis_obj = store.analysis(analysis_id)
    if analysis_obj is None:
        return abort(404)

    if request.method == "PUT":
        analysis_obj.update(request.json)
        store.commit()

    data = analysis_obj.to_dict()
    data["failed_jobs"] = [job_obj.to_dict() for job_obj in analysis_obj.failed_jobs]
    data["user"] = analysis_obj.user.to_dict() if analysis_obj.user else None
    return jsonify(**data)


@blueprint.route("/info")
def info():
    """Display meta data about database."""
    metadata_obj = store.info()
    return jsonify(**metadata_obj.to_dict())


@blueprint.route("/me")
def me():
    """Return information about a logged in user."""
    return jsonify(**g.current_user.to_dict())


@blueprint.route("/aggregate/jobs")
def aggregate_jobs():
    """Return stats about jobs."""
    days_back = int(request.args.get("days_back", 31))
    one_month_ago = datetime.datetime.now() - datetime.timedelta(days=days_back)

    data = store.aggregate_failed(one_month_ago)
    return jsonify(jobs=data)


@blueprint.route("/update-all")
def update_analyses():
    """Update all ongoing analysis by querying SLURM"""
    process = multiprocessing.Process(target=store.update_ongoing_analyses, kwargs={"ssh": True})
    process.start()
    return jsonify(f"Success! Trailblazer updated {datetime.datetime.now()}"), 201


@blueprint.route("/update/<int:analysis_id>", methods=["PUT"])
def update_analysis(analysis_id):
    """Update a specific analysis"""
    try:
        process = multiprocessing.Process(
            target=store.update_run_status, kwargs={"analysis_id": analysis_id, "ssh": True}
        )
        process.start()
        return jsonify("Success! Update request sent"), 201
    except Exception as e:
        return jsonify(f"Exception: {e}"), 409


@blueprint.route("/cancel/<int:analysis_id>", methods=["PUT"])
def cancel(analysis_id):
    """Cancel an analysis and all slurm jobs associated with it"""
    auth_header = request.headers.get("Authorization")
    jwt_token = auth_header.split("Bearer ")[-1]
    user_data = jwt.decode(jwt_token, verify=False)
    try:
        process = multiprocessing.Process(
            target=store.cancel_analysis,
            kwargs={"analysis_id": analysis_id, "email": user_data["email"], "ssh": True},
        )
        process.start()
        return jsonify("Success! Cancel request sent"), 201
    except Exception as e:
        return jsonify(f"Exception: {e}"), 409


@blueprint.route("/delete/<int:analysis_id>", methods=["PUT"])
def delete(analysis_id):
    """Cancel an analysis and all slurm jobs associated with it"""
    try:
        process = multiprocessing.Process(
            target=store.delete_analysis,
            kwargs={"analysis_id": analysis_id, "force": True},
        )
        process.start()
        return jsonify("Success! Delete request sent!"), 201
    except Exception as e:
        return jsonify(f"Exception: {e}"), 409


# CG REST INTERFACE ###
# ONLY POST routes which accept messages in specific format
# NOT for use with GUI (for now)


@blueprint.route("/query-analyses", methods=["POST"])
def post_query_analyses():
    """Return list of analyses matching the query terms"""
    content = request.json
    query_analyses = store.analyses(
        case_id=content.get("case_id"),
        query=content.get("query"),
        status=content.get("status"),
        deleted=content.get("deleted"),
        temp=content.get("temp"),
        before=parse_datestr(content.get("before")) if content.get("before") else None,
        is_visible=content.get("visible"),
        family=content.get("family"),
        data_analysis=content.get("data_analysis"),
    )
    data = [stringify_timestamps(analysis_obj.to_dict()) for analysis_obj in query_analyses]
    return jsonify(*data), 200


@blueprint.route("/get-latest-analysis", methods=["POST"])
def post_get_latest_analysis():
    """Return latest analysis entry for specified case"""
    content = request.json
    analysis_obj = store.get_latest_analysis(case_id=content.get("case_id"))
    if analysis_obj:
        data = stringify_timestamps(analysis_obj.to_dict())
        return jsonify(**data), 200
    return jsonify(None), 200


@blueprint.route("/find-analysis", methods=["POST"])
def post_find_analysis():
    """Find analysis using case_id, date, and status"""
    content = request.json
    analysis_obj = store.get_analysis(
        case_id=content.get("case_id"),
        started_at=parse_datestr(content.get("started_at")),
        status=content.get("status"),
    )
    if analysis_obj:
        data = stringify_timestamps(analysis_obj.to_dict())
        return jsonify(**data), 200
    return jsonify(None), 200


@blueprint.route("/delete-analysis", methods=["POST"])
def post_delete_analysis():
    """Delete analysis using analysis_id. If analysis is ongoing, error will be raised.
    To delete ongoing analysis, --force flag should also be passed.
    If an ongoing analysis is deleted in ths manner, all ongoing jobs will be cancelled"""
    content = request.json
    try:
        store.delete_analysis(analysis_id=content.get("analysis_id"), force=content.get("force"))
        return jsonify(None), 201
    except Exception as e:
        return jsonify(f"Exception: {e}"), 409


@blueprint.route("/mark-analyses-deleted", methods=["POST"])
def post_mark_analyses_deleted():
    """Mark all analysis belonging to a case deleted"""
    content = request.json
    old_analyses = store.mark_analyses_deleted(case_id=content.get("case_id"))
    data = [stringify_timestamps(analysis_obj.to_dict()) for analysis_obj in old_analyses]
    if data:
        return jsonify(*data), 201
    return jsonify(None), 201


@blueprint.route("/add-pending-analysis", methods=["POST"])
def post_add_pending_analysis():
    """Add new analysis with pending status"""
    content = request.json
    try:
        analysis_obj = store.add_pending_analysis(
            case_id=content.get("case_id"),
            email=content.get("email"),
            type=content.get("type"),
            config_path=content.get("config_path"),
            out_dir=content.get("out_dir"),
            priority=content.get("priority"),
            data_analysis=content.get("data_analysis"),
            ticket_id=content.get("ticket"),
        )
        data = stringify_timestamps(analysis_obj.to_dict())
        return jsonify(**data), 201
    except Exception as e:
        return jsonify(f"Exception: {e}"), 409


@blueprint.route("/set-analysis-uploaded", methods=["PUT"])
def put_set_analysis_uploaded():
    content: Response.json = request.json

    try:
        store.set_analysis_uploaded(
            case_id=content.get("case_id"), uploaded_at=content.get("uploaded_at")
        )
        return jsonify("Success! Update request sent"), 201
    except Exception as error:
        return jsonify(f"Exception: {error}"), 409
