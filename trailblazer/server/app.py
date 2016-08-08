# -*- coding: utf-8 -*-
import os

from flask import abort, Flask, render_template, request, redirect
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap
import sqlalchemy as sqa

from trailblazer.store import Analysis, Model

app = Flask(__name__)
DEBUG = False
SECRET_KEY = os.environ.get('TRAILBLAZER_SECRET_KEY') or 'thisIsNotSecret!'
BOOTSTRAP_SERVE_LOCAL = True
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
    recent_query = (Analysis.query.filter_by(status='completed')
                                  .order_by(Analysis.started_at.desc())
                                  .limit(10))
    fail_query = (Analysis.query.filter_by(status='failed')
                                .order_by(Analysis.started_at.desc())
                                .limit(20))
    running_query = (Analysis.query.filter_by(status='running')
                                   .order_by(Analysis.started_at.desc()))
    return render_template('index.html', fails=fail_query,
                           runnings=running_query, recents=recent_query)


@app.route('/analyses')
def analyses():
    """Show all analyses."""
    page_num = int(request.args.get('page', 1))
    query_str = request.args.get('query_str')
    query = Analysis.query.order_by(Analysis.started_at.desc())
    if query_str:
        query = query.filter(sqa.or_(Analysis.case_id.contains(query_str),
                                     Analysis.status == query_str))
    page = query.paginate(page=page_num, per_page=30)
    return render_template('analyses.html', analyses=page, query_str=query_str)


@app.route('/analyses/<case_id>')
def analysis(case_id):
    """Show history for an analysis."""
    analyses = (Analysis.query.filter_by(case_id=case_id)
                              .order_by(Analysis.started_at.desc()))
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
