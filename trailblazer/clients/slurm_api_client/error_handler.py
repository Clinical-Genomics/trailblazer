import logging
from functools import wraps
from pydantic import ValidationError
from requests import ConnectionError, HTTPError
from requests.exceptions import MissingSchema

from trailblazer.exc import InvalidSlurmResponseError, SlurmRequestFailed

LOG = logging.getLogger(__name__)


def handle_client_errors(func):
    """Handle errors that may occur when interacting with the slurm API.

    Raises:
        SlurmAPIClientError
        SlurmRequestFailed: when the request to the slurm fails.
        InvalidSlurmResponse: when the returned data from the slurm is invalid.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (MissingSchema, HTTPError, ConnectionError) as error:
            LOG.error(f"Request against slurm failed: {error}, {error.response.text}")
            raise SlurmRequestFailed("Request against slurm failed")
        except ValidationError as error:
            LOG.error(f"Invalidly formatted response from slurm: {error}")
            raise InvalidSlurmResponseError("Invalidly formatted response from slurm")

    return wrapper
