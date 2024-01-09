import datetime
from flask import Request

from trailblazer.dto.analysis_request import AnalysisRequest


def parse_analysis_request(request: Request) -> AnalysisRequest:
    """Parse a request for retrieving analyses."""
    query_params = {}
    for key in request.args.keys():
        if key.endswith("[]"):
            query_params[key[:-2]] = request.args.getlist(key)
        else:
            query_params[key] = request.args.get(key)
    return AnalysisRequest.model_validate(query_params)


def stringify_timestamps(data: dict) -> dict[str, str]:
    """Convert datetime into string before dumping in order to avoid information loss"""
    for key, val in data.items():
        if isinstance(val, datetime.datetime):
            data[key] = str(val)
    return data
