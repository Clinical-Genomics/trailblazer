# -*- coding: utf-8 -*-
import datetime

from flask import abort, g, Blueprint, jsonify, make_response, request, Response
from google.auth import jwt

from trailblazer.server.ext import store

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")


@blueprint.before_request
def before_request():
    if request.method == "OPTIONS":
        return make_response(jsonify(ok=True), 204)
    auth_header = request.headers.get("Authorization")
    if auth_header:
        jwt_token = auth_header.split("Bearer ")[-1]
    else:
        return abort(403, "no JWT token found on request")
    user_data = jwt.decode(jwt_token, verify=False)
    user_obj = store.user(user_data["email"])
    if user_obj is None:
        return abort(403, f"{user_data['email']} doesn't have access")
    g.current_user = user_obj


@blueprint.route("/analyses")
def analyses():
    """Display analyses."""
    per_page = int(request.args.get("per_page", 50))
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


# CG REST INTERFACE ###


@blueprint.route("/query-analyses", methods=["POST"])
def post_query_analyses():
    content = request.json
    query_analyses = store.analyses(
        case_id=content.get("case_id"),
        query=content.get("query"),
        status=content.get("status"),
        deleted=content.get("deleted"),
        temp=content.get("temp"),
        before=content.get("before"),
        is_visible=content.get("visible"),
        family=content.get("family"),
    )
    data = [analysis_obj.to_dict() for analysis_obj in query_analyses]
    return jsonify(*data), 200


@blueprint.route("/get-latest-analysis", methods=["POST"])
def post_get_latest_analysis():
    content = request.json
    analysis_obj = store.get_latest_analysis(case_id=content.get("case_id"))
    if analysis_obj:
        data = analysis_obj.to_dict()
        return jsonify(**data), 200
    return jsonify(None), 200


@blueprint.route("/find-analysis", methods=["POST"])
def post_find_analysis():
    content = request.json
    analysis_obj = store.find_analysis(
        case_id=content.get("case_id"),
        started_at=content.get("started_at"),
        status=content.get("started"),
    )
    if analysis_obj:
        data = analysis_obj.to_dict()
        return Response(jsonify(**data), status=200, mimetype="application/json")
    return Response(jsonify(None), status=200, mimetype="application/json")


@blueprint.route("/delete-analysis", methods=["POST"])
def post_delete_analysis():
    content = request.json
    try:
        analysis_obj = store.delete_analysis(
            case_id=content.get("case_id"), started_at=content.get("started_at")
        )
        data = analysis_obj.to_dict()
        return Response(jsonify(**data), 201, mimetype="application/json")
    except Exception as e:
        return Response(jsonify(f"Exception: {e}"), 409, mimetype="application/json")


@blueprint.route("/mark-analyses-deleted", methods=["POST"])
def post_mark_analyses_deleted():
    content = request.json
    old_analyses = store.mark_analyses_deleted(case_id=content.get("case_id"))
    data = [analysis_obj for analysis_obj in old_analyses]
    if data:
        return Response(jsonify(*data), 201, mimetype="application/json")
    return Response(jsonify(None), 201, mimetype="application/json")


@blueprint.route("/add-pending-analysis", methods=["POST"])
def post_add_pending_analysis():
    content = request.json
    analysis_obj = store.add_pending_analysis(
        case_id=content.get("case_id"), email=content.get("email")
    )
    data = analysis_obj.to_dict()
    return Response(jsonify(**data), 201, mimetype="application/json")
