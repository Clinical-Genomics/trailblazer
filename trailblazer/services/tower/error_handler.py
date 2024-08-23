import logging
from functools import wraps

from trailblazer.exc import TowerAPIClientError
from trailblazer.exceptions import TowerServiceError, TowerWorkflowIdFileMissing

LOG = logging.getLogger(__name__)


def handle_tower_service_errors(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as error:
            LOG.error(f"Workflow id file not found in tower service: {error}")
            raise TowerWorkflowIdFileMissing()
        except TowerAPIClientError as error:
            raise TowerServiceError("Error in tower API client")

    return wrapper
