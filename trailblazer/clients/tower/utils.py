import logging
from functools import wraps
from pydantic import ValidationError
from requests import ConnectionError, HTTPError
from requests.exceptions import MissingSchema

from trailblazer.exc import InvalidTowerAPIResponse, TowerAPIClientError, TowerRequestFailed

LOG = logging.getLogger(__name__)


def handle_client_errors(func):
    """Handle errors that may occur when interacting with the Tower API.

    Raises:
        TowerRequestFailed: when the request to the Tower API fails.
        InvalidTowerAPIResponse: when the returned data from the Tower API is invalid.
        TowerAPIClientError: when an unexpected error occurs in the Tower API client.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (MissingSchema, HTTPError, ConnectionError) as error:
            LOG.error(f"Request against tower failed: {error}, {error.response.text}")
            raise TowerRequestFailed(error) from error
        except ValidationError as error:
            LOG.error(f"Invalidly formatted response from Tower API: {error}")
            raise InvalidTowerAPIResponse(error) from error
        except Exception as error:
            LOG.error(f"Unexpected error in Tower API client: {error}")
            raise TowerAPIClientError(error) from error

    return wrapper
