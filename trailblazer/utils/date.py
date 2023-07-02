from datetime import datetime, timedelta


def get_date_days_ago(days_ago: int) -> datetime:
    """Return the date that was number of 'days_ago'."""
    return datetime.now() - timedelta(days=days_ago)