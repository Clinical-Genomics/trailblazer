from functools import wraps
import logging

from pydantic import ValidationError
from requests import HTTPError


from trailblazer.exc import ResponseDeserializationError, SlurmAPIClientError

LOG = logging.getLogger(__name__)


def handle_errors(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            LOG.error(f"Error for request in slurm API client: {e.response.content}")
            raise SlurmAPIClientError()
        except ValidationError as e:
            LOG.error(f"Error deserializing slurm API response: {e}")
            raise ResponseDeserializationError()

    return wrapper
