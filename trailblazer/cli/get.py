import click


@click.command("get")
@click.option("-c", "--comment", help="return analyses with comments containing")
@click.pass_context
def get(context, comment):
    """Display recent logs for analyses."""
    runs = context.obj["store"].find_analyses_with_comment(comment=comment).limit(100)
    for run_obj in runs:
        if run_obj.status == "pending":
            message = f"{run_obj.id} | {run_obj.family} [{run_obj.status.upper()}]"
        else:
            message = (
                f"{run_obj.id} | {run_obj.family} {run_obj.started_at.date()} "
                f"[{run_obj.type.upper()}/{run_obj.status.upper()}]"
            )
            if run_obj.status == "running":
                message = click.style(
                    f"{message} - {run_obj.progress * 100}/100", fg="blue"
                )
            elif run_obj.status == "completed":
                message = click.style(f"{message} - {run_obj.completed_at}", fg="green")
            elif run_obj.status == "failed":
                message = click.style(message, fg="red")

            message += f" {run_obj.comment}"
        click.echo(message)
