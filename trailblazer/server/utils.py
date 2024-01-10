import datetime
from flask import Request

from trailblazer.dto import AnalysesRequest, AnalysisUpdateRequest, FailedJobsRequest


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


def parse_analysis_update_request(request: Request) -> AnalysisUpdateRequest:
    return AnalysisUpdateRequest.model_validate(request.json)


def parse_get_failed_jobs_request(request: Request) -> FailedJobsRequest:
    return FailedJobsRequest.model_validate(request.args)


def stringify_timestamps(data: dict) -> dict[str, str]:
    """Convert datetime into string before dumping in order to avoid information loss"""
    for key, val in data.items():
        if isinstance(val, datetime.datetime):
            data[key] = str(val)
    return data
