# -*- coding: utf-8 -*-
from flask import abort, Blueprint, jsonify, request

from trailblazer.server.ext import store

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')


@blueprint.route('/analyses')
def analyses():
    """Display analyses."""
    per_page = int(request.args.get('per_page', 30))
    page = int(request.args.get('page', 1))
    query = store.analyses(status=request.args.get('status')).paginate(page, per_page=per_page)

    data = []
    for analysis_obj in query.items:
        analysis_data = analysis_obj.to_dict()
        analysis_data['user'] = analysis_obj.user.to_dict() if analysis_obj.user else None
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
