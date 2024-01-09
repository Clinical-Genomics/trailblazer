import datetime
from flask import Request

from trailblazer.dto.analyses_request import AnalysesRequest
from trailblazer.server.schemas import AnalysisUpdateRequest


def parse_analyses_request(request: Request) -> AnalysesRequest:
    """Parse a request for retrieving analyses."""
    query_params = {}
    for key in request.args.keys():
        if key.endswith("[]"):
            query_params[key[:-2]] = request.args.getlist(key)
        else:
            query_params[key] = request.args.get(key)
    return AnalysesRequest.model_validate(query_params)


def parse_analysis_update_request(request: Request) -> AnalysisUpdateRequest:
    return AnalysisUpdateRequest.model_validate(request.json)


def stringify_timestamps(data: dict) -> dict[str, str]:
    """Convert datetime into string before dumping in order to avoid information loss"""
    for key, val in data.items():
        if isinstance(val, datetime.datetime):
            data[key] = str(val)
    return data
