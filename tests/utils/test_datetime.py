from datetime import datetime

import pytest

from trailblazer.utils.datetime import (
    convert_days_to_minutes,
    convert_timestamp_to_minutes,
    get_date_number_of_days_ago,
    get_datetime_from_timestamp,
    tower_datetime_converter,
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

    # THEN the return is number of minutes corresponding to the number of days
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

    # THEN the return is number of minutes corresponding to timestamp
    assert minutes == expected_minutes


def test_get_datetime_from_timestamp():
    """Test returning a datetime object from a timestamp."""

    # GIVEN a timestamp

    # WHEN calling the function
    date: datetime = get_datetime_from_timestamp(
        timestamp="23:59:59", datetime_formats=["%H:%M:%S"]
    )

    # THEN the return should be a datetime object
    assert isinstance(date, datetime)


def test_get_datetime_from_timestamp_with_invalid_timestamp(caplog):
    """Test returning a datetime object from a timestamp, which is invalid."""

    # GIVEN a timestamp

    # WHEN calling the function
    get_datetime_from_timestamp(timestamp="not a timestamp", datetime_formats=["%H:%M:%S"])

    # THEN log the error
    assert "Error converting timestamp" in caplog.text


def test_get_date_number_of_days_ago(timestamp_now: datetime):
    """Test returning a date corresponding to number of days ago."""

    # GIVEN days ago

    # WHEN calling the function
    date: datetime = get_date_number_of_days_ago(number_of_days_ago=1)

    # THEN the return should be a date
    assert isinstance(date, datetime)

    # Then the date returned should be less than then today
    assert date < timestamp_now


@pytest.mark.parametrize(
    "datetime_stamp",
    ["2023-04-04T08:11:24Z", "2023-06-20T08:01:57.661819Z", "2023-09-14T11:14:55.664772403Z"],
)
def test_tower_datetime_converter(datetime_stamp: str):
    """Test parsing a Tower datetime stamp."""

    # GIVEN datetime stamps

    # WHEN calling the function
    date: datetime = tower_datetime_converter(datetime_stamp=datetime_stamp)

    # THEN the return should be a date
    assert isinstance(date, datetime)
