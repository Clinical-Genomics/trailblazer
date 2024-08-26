from functools import wraps
import logging

from pydantic import ValidationError
import requests

from trailblazer.exc import ResponseDeserializationError, SlurmAPIClientError

LOG = logging.getLogger(__name__)


def handle_errors(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            LOG.error(f"Error getting job: {e.response.content}")
            raise SlurmAPIClientError(e)
        except ValidationError as e:
            LOG.error(f"Error deserializing job response: {e}")
            raise ResponseDeserializationError(e)

    return wrapper
