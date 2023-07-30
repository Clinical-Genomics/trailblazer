from datetime import datetime
from typing import List

from trailblazer.constants import (
    TOWER_TIMESTAMP_FORMAT,
    TOWER_TIMESTAMP_FORMAT_ALTERNATIVE,
    MINUTES_PER_HOUR,
    HOURS_IN_DAY,
    SECONDS_PER_MINUTE,
)


def convert_days_to_minutes(days_nr: int) -> int:
    """Converts number of days to minutes."""
    return days_nr * HOURS_IN_DAY * MINUTES_PER_HOUR


def convert_timestamp_to_minutes(timestamp: datetime) -> int:
    """Converts timestamp to minutes."""
    zero_seconds: datetime = datetime.strptime("0:0:0", "%H:%M:%S")
    return int((timestamp - zero_seconds).total_seconds() / SECONDS_PER_MINUTE)


def get_datetime_from_timestamp(timestamp: str, datetime_formats: List[str]) -> datetime:
    """Converts a timestamp into a datatime object."""
    for datetime_format in datetime_formats:
        try:
            return datetime.strptime(timestamp, datetime_format)
        except ValueError:
            continue


def tower_datetime_converter(timestamp: str) -> datetime:
    """Converts a NF Tower timestamp into a datatime object."""
    allowed_formats = [TOWER_TIMESTAMP_FORMAT, TOWER_TIMESTAMP_FORMAT_ALTERNATIVE]
    return get_datetime_from_timestamp(timestamp, allowed_formats)
