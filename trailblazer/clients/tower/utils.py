from functools import wraps
from pydantic import ValidationError
from requests import ConnectionError, HTTPError
from requests.exceptions import MissingSchema

from trailblazer.exc import InvalidTowerAPIResponse, TowerAPIClientError, TowerRequestFailed


def handle_client_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (MissingSchema, HTTPError, ConnectionError) as error:
            raise TowerRequestFailed(f"Request failed against Tower API: {error}")
        except ValidationError as error:
            raise InvalidTowerAPIResponse(f"Unexpected response data from Tower API: {error}")
        except Exception as error:
            raise TowerAPIClientError(f"Unexpected error from Tower API client: {error}")

    return wrapper
