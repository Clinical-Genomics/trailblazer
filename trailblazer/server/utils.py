import datetime
import logging
from functools import wraps
from http import HTTPStatus

from flask import Request, jsonify
from pydantic import ValidationError

from trailblazer.dto import AnalysesRequest
from trailblazer.exc import (
    CancelSlurmAnalysisNotSupportedError,
    MissingAnalysis,
    WorkblockConfigurationConflictError,
)
from trailblazer.services.authentication_service.exceptions import AuthenticationError

LOG = logging.getLogger(__name__)


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


def handle_endpoint_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthenticationError:
            return jsonify("User not allowed"), HTTPStatus.FORBIDDEN
        except MissingAnalysis as error:
            return jsonify(error=str(error)), HTTPStatus.NOT_FOUND
        except CancelSlurmAnalysisNotSupportedError as error:
            return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST
        except ValidationError as error:
            LOG.error(f"Validation error in analysis endpoint: {error}")
            return jsonify(error=str(error)), HTTPStatus.BAD_REQUEST
        except WorkblockConfigurationConflictError as error:
            LOG.error(f"Workblock configuration conflict: {error}")
            return jsonify(error=str(error)), HTTPStatus.CONFLICT
        except Exception as error:
            LOG.error(f"Unexpected error in analysis endpoint: {error}")
            return (
                jsonify(error="An error occurred while processing your request."),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    return wrapper
