import datetime
from flask import Request

from trailblazer.dto import AnalysesRequest


def parse_analyses_request(request: Request) -> AnalysesRequest:
    """Parse a request for retrieving analyses."""
    query_params = {}
    for key in request.args.keys():
        if key_has_list_of_values(key):
            query_params[key[:-2]] = request.args.getlist(key)
        else:
            query_params[key] = request.args.get(key)
    return AnalysesRequest.model_validate(query_params)


def key_has_list_of_values(key: str) -> bool:
    return key.endswith("[]")


def stringify_timestamps(data: dict) -> dict[str, str]:
    """Convert datetime into string before dumping in order to avoid information loss"""
    for key, val in data.items():
        if isinstance(val, datetime.datetime):
            data[key] = str(val)
    return data
