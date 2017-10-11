from pathlib import Path
import shutil

import click


@click.command()
@click.option('-f', '--force', is_flag=True, help='skip sanity checks')
@click.option('-y', '--yes', is_flag=True, help='skip manual confirmations')
@click.argument('analysis_id', type=int)
@click.pass_context
def delete(context, force, yes, analysis_id):
    """Delete an analysis log from the database."""
    analysis_obj = context.obj['store'].analysis(analysis_id)
    if analysis_obj is None:
        print(click.style('analysis log not found', fg='red'))
        context.abort()

    print(click.style(f"{analysis_obj.family}: {analysis_obj.status}"))

    if analysis_obj.is_temp:
        if yes or click.confirm(f"remove analysis log?"):
            analysis_obj.delete()
            context.obj['store'].commit()
            print(click.style(f"analysis deleted: {analysis_obj.family}", fg='blue'))
    else:
        if analysis_obj.is_deleted:
            print(click.style(f"{analysis_obj.family}: already deleted", fg='red'))
            context.abort()

        if Path(analysis_obj.out_dir).exists():
            root_dir = context.obj['store'].families_dir
            family_dir = analysis_obj.out_dir
            if not force and (len(family_dir) <= len(root_dir) or root_dir not in family_dir):
                print(click.style(f"unknown analysis output dir: {analysis_obj.out_dir}", fg='red'))
                print(click.style("use '--force' to override"))
                context.abort()

            if yes or click.confirm(f"remove analysis output: {analysis_obj.out_dir}?"):
                shutil.rmtree(analysis_obj.out_dir, ignore_errors=True)
                analysis_obj.is_deleted = True
                context.obj['store'].commit()
                print(click.style(f"analysis deleted: {analysis_obj.family}", fg='blue'))
        else:
            print(click.style(f"analysis output doesn't exist: {analysis_obj.out_dir}", fg='red'))
            context.abort()
