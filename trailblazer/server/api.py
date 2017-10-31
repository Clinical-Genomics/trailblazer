# -*- coding: utf-8 -*-
from flask import abort, g, Blueprint, jsonify, make_response, request
from google.auth import jwt

from trailblazer.server.ext import store

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')


@blueprint.before_request
def before_request():
    if request.method == 'OPTIONS':
        return make_response(jsonify(ok=True), 204)
    auth_header = request.headers.get('Authorization')
    if auth_header:
        jwt_token = auth_header.split('Bearer ')[-1]
    else:
        return abort(403, 'no JWT token found on request')
    user_data = jwt.decode(jwt_token, verify=False)
    user_obj = store.user(user_data['email'])
    if user_obj is None:
        return abort(403, f"{user_data['email']} doesn't have access")
    g.current_user = user_obj


@blueprint.route('/analyses')
def analyses():
    """Display analyses."""
    per_page = int(request.args.get('per_page', 50))
    page = int(request.args.get('page', 1))
    query = store.analyses(status=request.args.get('status'),
                           query=request.args.get('query'),
                           is_visible=request.args.get('is_visible') == 'true' or None)

    query_page = query.paginate(page, per_page=per_page)
    data = []
    for analysis_obj in query_page.items:
        analysis_data = analysis_obj.to_dict()
        analysis_data['user'] = analysis_obj.user.to_dict() if analysis_obj.user else None
        analysis_data['failed_jobs'] = [job_obj.to_dict() for job_obj in analysis_obj.failed_jobs]
        data.append(analysis_data)

    return jsonify(analyses=data)


@blueprint.route('/analyses/<int:analysis_id>', methods=['GET', 'PUT'])
def analysis(analysis_id):
    """Display a single analysis."""
    analysis_obj = store.analysis(analysis_id)
    if analysis_obj is None:
        return abort(404)

    if request.method == 'PUT':
        analysis_obj.update(request.json)
        store.commit()

    data = analysis_obj.to_dict()
    data['failed_jobs'] = [job_obj.to_dict() for job_obj in analysis_obj.failed_jobs]
    data['user'] = analysis_obj.user.to_dict() if analysis_obj.user else None
    return jsonify(**data)


@blueprint.route('/info')
def info():
    """Display meta data about database."""
    metadata_obj = store.info()
    return jsonify(**metadata_obj.to_dict())


@blueprint.route('/me')
def me():
    """Return information about a logged in user."""
    return jsonify(**g.current_user.to_dict())


@blueprint.route('/aggregate/jobs')
def aggregate_jobs():
    """Return stats about jobs."""
    data = store.aggregate_failed()
    return jsonify(jobs=data)
