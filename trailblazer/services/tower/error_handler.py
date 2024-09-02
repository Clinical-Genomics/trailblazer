from functools import wraps
import logging

from trailblazer.exc import TowerAPIClientError, TowerServiceError, WorkflowIdFileMissingError

LOG = logging.getLogger(__name__)


def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as error:
            LOG.error(f"File not found: {error}")
            raise WorkflowIdFileMissingError()
        except TowerAPIClientError as error:
            raise TowerServiceError(error) from error

    return wrapper
