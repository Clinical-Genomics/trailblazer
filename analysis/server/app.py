# -*- coding: utf-8 -*-
import os

from flask import abort, Flask, render_template, request, redirect
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap

from analysis.store import Analysis, Model

app = Flask(__name__)
DEBUG = False
SECRET_KEY = os.environ.get('ANALYSIS_SECRET_KEY') or 'daopkdpowanvigjråepl'
BOOTSTRAP_SERVE_LOCAL = True
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test-init.sqlite3'
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
    error_query = (Analysis.query.filter_by(status='errored')
                                 .order_by(Analysis.started_at.desc())
                                 .limit(10))
    running_query = (Analysis.query.filter_by(status='running')
                                   .order_by(Analysis.started_at.desc()))
    return render_template('index.html', errors=error_query,
                           runnings=running_query, recents=recent_query)


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
