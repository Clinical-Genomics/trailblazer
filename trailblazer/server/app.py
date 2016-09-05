# -*- coding: utf-8 -*-
"""Flask app module."""
import logging
import os

from flask import abort, Flask, render_template, request, redirect
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap
import sqlalchemy as sqa

from trailblazer.store import Analysis, Model, Metadata, api

log = logging.getLogger(__name__)

app = Flask(__name__)
application = app
SECRET_KEY = os.environ.get('TRAILBLAZER_SECRET_KEY') or 'thisIsNotSecret!'
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
if 'mysql' in SQLALCHEMY_DATABASE_URI:  # pragma: no cover
    SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False
TEMPLATES_AUTO_RELOAD = True
app.config.from_object(__name__)

Bootstrap(app)
db = Alchy(app, Model=Model)


@app.route('/')
def index():
    """Dashboard view."""
    metadata = Metadata.query.first()
    recent_query = api.analyses(status='completed').limit(10)
    fail_query = (api.analyses(status='failed')
                     .filter(Analysis.comment == None).limit(20))
    running_query = api.analyses(status=['running', 'pending'])
    return render_template('index.html', fails=fail_query,
                           runnings=running_query, recents=recent_query,
                           metadata=metadata)


@app.route('/analyses')
def analyses():
    """Show all analyses."""
    page_num = int(request.args.get('page', 1))
    query_str = request.args.get('query_str')
    query = api.analyses()
    if query_str:
        query = query.filter(sqa.or_(Analysis.case_id.contains(query_str),
                                     Analysis.status == query_str))
    page = query.paginate(page=page_num, per_page=30)
    return render_template('analyses.html', analyses=page, query_str=query_str)


@app.route('/analyses/<case_id>')
def analysis(case_id):
    """Show history for an analysis."""
    analyses = api.analyses(analysis_id=case_id)
    return render_template('analysis.html', analyses=analyses, case_id=case_id)


@app.route('/comments/<analysis_id>', methods=['POST'])
def comments(analysis_id):
    """Interact with comments."""
    analysis_obj = Analysis.query.get(analysis_id)
    if analysis_obj is None:
        return abort(404)
    new_comment = request.form['comment']
    analysis_obj.comment = new_comment
    db.commit()
    return redirect(request.referrer)


@app.route('/analyses/<analysis_id>/status', methods=['POST'])
def update_status(analysis_id):
    """Update the status of an analysis."""
    new_status = request.form['status']
    analysis_obj = Analysis.query.get(analysis_id)
    log.info("updating '%s' status: %s -> %s", analysis_obj.id,
             analysis_obj.status, new_status)
    analysis_obj.status = new_status
    db.commit()
    return redirect(request.referrer)
