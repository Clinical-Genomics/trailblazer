import logging
from functools import wraps

from trailblazer.exceptions import (
    JobServiceError,
    SlurmAPIServiceError,
    SlurmCLIServiceError,
    TowerServiceError,
)

LOG = logging.getLogger(__name__)


def handle_job_service_errors(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (SlurmAPIServiceError, SlurmCLIServiceError, TowerServiceError) as error:
            LOG.error(f"Workflow manager error in job service: {error}")
            raise JobServiceError(error) from error
        except Exception as error:
            LOG.error(f"Unexpected error in job service: {error}")
            raise JobServiceError(f"Unexpected error: {error}") from error

    return wrapper
