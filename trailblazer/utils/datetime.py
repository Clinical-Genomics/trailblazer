from datetime import datetime
from typing import List, Optional

from trailblazer.constants import TOWER_TIMESTAMP_FORMAT, TOWER_TIMESTAMP_FORMAT_ALTERNATIVE


def datetime_converter(timestamp: str, allowed_formats: List[str]) -> datetime:
    """Converts a timestamp into a datatime object."""
    for dt_format in allowed_formats:
        try:
            return datetime.strptime(timestamp, dt_format)
        except ValueError:
            continue


def tower_datetime_converter(timestamp: str) -> datetime:
    """Converts a NF Tower timestamp into a datatime object."""
    allowed_formats = [TOWER_TIMESTAMP_FORMAT, TOWER_TIMESTAMP_FORMAT_ALTERNATIVE]
    return datetime_converter(timestamp, allowed_formats)
