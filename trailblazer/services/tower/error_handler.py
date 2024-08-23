import logging
from functools import wraps

from trailblazer.exc import TowerAPIClientError
from trailblazer.exceptions import TowerServiceError

LOG = logging.getLogger(__name__)


def handle_tower_service_errors(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TowerAPIClientError as error:
            raise TowerServiceError(error) from error

    return wrapper
