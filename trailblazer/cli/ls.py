import click
from dateutil.parser import parse as parse_date

from trailblazer.store.models import STATUS_OPTIONS


@click.command('ls')
@click.option('-s', '--status', type=click.Choice(STATUS_OPTIONS))
@click.option('-b', '--before', help='return analyses started before date')
@click.pass_context
def ls_cmd(context, before, status):
    """Display recent logs for analyses."""
    runs = context.obj['store'].analyses(
        status=status,
        deleted=False,
        before=parse_date(before) if before else None,
    ).limit(30)
    for run_obj in runs:
        if run_obj.status == 'pending':
            message = f"{run_obj.id} | {run_obj.family} [{run_obj.status.upper()}]"
        else:
            message = (f"{run_obj.id} | {run_obj.family} {run_obj.started_at.date()} "
                       f"[{run_obj.type.upper()}/{run_obj.status.upper()}]")
            if run_obj.status == 'running':
                message = click.style(f"{message} - {run_obj.progress * 100}/100", fg='blue')
            elif run_obj.status == 'completed':
                message = click.style(f"{message} - {run_obj.completed_at}", fg='green')
            elif run_obj.status == 'failed':
                message = click.style(message, fg='red')
        print(message)
