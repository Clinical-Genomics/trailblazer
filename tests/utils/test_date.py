from datetime import datetime

from trailblazer.utils.date import get_date_days_ago


def test_get_date_days_ago(timestamp_now: datetime):
    """Test returning a date corresponding to number of days ago."""

    # GIVEN days ago

    # WHEN calling the function
    date: datetime = get_date_days_ago(days_ago=1)

    # THEN assert the return should be a date
    assert isinstance(date, datetime)

    # Then the date returned should be less than then today
    assert date < timestamp_now
