import logging
from functools import wraps

from trailblazer.exc import AnalysisServiceError
from trailblazer.exceptions import JobServiceError

LOG = logging.getLogger(__name__)


def handle_analysis_service_errors(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except JobServiceError as error:
            raise AnalysisServiceError(error) from error

    return wrapper
