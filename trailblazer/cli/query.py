import click
from trailblazer.store.api import Store as TrailblazerAPI
import sys
import ruamel.yaml


@click.group("query", invoke_without_command=True)
@click.pass_context
def query(context):
    context.obj["api"] = TrailblazerAPI(context.obj["database"], context.obj["root"])


@query.command("check-analysis-running")
@click.argument("case_id", type=str)
@click.pass_context
def check_analysis_running(context, case_id):
    """Responds whether analysis is ongoing"""
    response = context.obj["api"].is_latest_analysis_ongoing(case_id=case_id)
    sys.stdout(response)
    sys.exit(0)


@query.command("mark-analyses-deleted")
@click.argument("case_id", type=str)
@click.pass_context
def mark_analyses_deleted(context, case_id):
    """Mark old analyses deleted"""
    for old_analysis in context.obj["api"].analyses(family=case_id):
        old_analysis.is_deleted = True
    context.obj["api"].commit()
    sys.exit(0)


@query.command("add-pending-analysis")
@click.argument("case_id", type=str)
@click.pass_context
def add_pending_analysis(context, case_id: str, email: str):
    context.obj["api"].add_pending(case_id=case_id, email=email)
    sys.exit(0)


@query.command("has-analysis-started")
@click.argument("case_id", type=str)
@click.pass_context
def has_analysis_started(context, case_id):
    started_statuses = {"ongoing", "failed", "completed"}
    analysis = context.obj["api"].analyses(family=case_id).first()
    if not analysis or analysis.status not in started_statuses:
        response = False
    elif analysis.status in started_statuses:
        response = True
    sys.stdout(response)


@query.command("get-analysis-status")
@click.argument("case_id", type=str)
@click.pass_context
def get_analysis_status(context, case_id):
    response = context.obj["api"].get_analysis_status(family=case_id)
    sys.stdout(response)
