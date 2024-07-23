from functools import wraps
from requests import ConnectionError, HTTPError
from requests.exceptions import MissingSchema

from trailblazer.exc import TowerAPIClientError


def handle_client_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (MissingSchema, HTTPError, ConnectionError) as error:
            raise TowerAPIClientError(f"Request failed: {error}")
        except Exception as error:
            raise TowerAPIClientError(f"Unexpected error, request failed: {error}")
    return wrapper
