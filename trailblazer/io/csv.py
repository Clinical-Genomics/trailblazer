"""Module for reading and writing comma separated values (CSV) formatted files."""
import csv
from typing import List


def read_csv_stream(stream: bytes, read_to_dict: bool = False) -> List[List[str]]:
    """Read CSV formatted stream."""
    csv_reader = (
        csv.DictReader(stream.splitlines()) if read_to_dict else csv.reader(stream.splitlines())
    )
    return list(csv_reader)
