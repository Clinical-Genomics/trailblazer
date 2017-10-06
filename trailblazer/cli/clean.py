import datetime as dt
import logging

import click
from .delete import delete

LOG = logging.getLogger(__name__)


@click.command()
@click.option('-y', '--yes', is_flag=True, help='skip manual confirmations')
@click.option('-d', '--days-ago', default=14, help='days ago analyses were started')
@click.pass_context
def clean(context, days_ago, yes):
    """Clean up files from "old" analyses runs."""
    number_of_days_ago = dt.datetime.now() - dt.timedelta(days=days_ago)
    analyses = context.obj['store'].analyses(
        status='completed',
        before=number_of_days_ago,
        deleted=False,
    )
    for analysis_obj in analyses:
        LOG.debug(f"checking analysis: {analysis_obj.family} ({analysis_obj.id})")
        latest_analysis = context.obj['store'].analyses(family=analysis_obj.family).first()
        if analysis_obj != latest_analysis:
            print(click.style(f"{analysis_obj.family}: family has been re-started", fg='yellow'))
        else:
            print(f"delete analysis: {analysis_obj.family} ({analysis_obj.id})")
            context.invoke(delete, analysis_id=analysis_obj.id, yes=yes)
