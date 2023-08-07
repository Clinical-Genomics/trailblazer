import pytest

from datetime import datetime

from trailblazer.utils.datetime import (
    get_date_days_ago,
    convert_days_to_minutes,
    convert_timestamp_to_minutes,
)

NUMBER_OF_MINUTES_IN_TWO_DAYS: int = 2880
MAX_NR_MINUTES_IN_TIMESTAMP: int = 1439


@pytest.mark.parametrize(
    "nr_of_days, expected_minutes",
    [(0, 0), (2, NUMBER_OF_MINUTES_IN_TWO_DAYS)],
)
def test_convert_days_to_minutes(nr_of_days: int, expected_minutes: int):
    """Test converting days to minutes."""

    # GIVEN days

    # WHEN calling the function
    minutes: int = convert_days_to_minutes(days_nr=nr_of_days)

    # THEN assert the return is number of minutes corresponding to the number of days
    assert minutes == expected_minutes


@pytest.mark.parametrize(
    "timestamp, expected_minutes",
    [
        (datetime.strptime("0:0:0", "%H:%M:%S"), 0),
        (datetime.strptime("23:59:59", "%H:%M:%S"), MAX_NR_MINUTES_IN_TIMESTAMP),
    ],
)
def test_convert_timestamp_to_minutes(timestamp: datetime, expected_minutes: int):
    """Test converting timestamp to minutes."""

    # GIVEN timestamps

    # WHEN calling the function
    minutes: int = convert_timestamp_to_minutes(timestamp=timestamp)

    # THEN assert the return is number of minutes corresponding to timestamp
    assert minutes == expected_minutes


def test_get_date_days_ago(timestamp_now: datetime):
    """Test returning a date corresponding to number of days ago."""

    # GIVEN days ago

    # WHEN calling the function
    date: datetime = get_date_days_ago(days_ago=1)

    # THEN assert the return should be a date
    assert isinstance(date, datetime)

    # Then the date returned should be less than then today
    assert date < timestamp_now
