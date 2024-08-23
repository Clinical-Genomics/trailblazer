class TrailblazerError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"TrailblazerError: {self.message}"


class MissingAnalysis(TrailblazerError):
    """Error for missing analysis"""


class MissingJob(TrailblazerError):
    """Error for missing job"""


class CancelSlurmAnalysisNotSupportedError(TrailblazerError):
    def __init__(self):
        self.message = "Cancelling SLURM analysis via the web app is not supported"


class MissingFileError(TrailblazerError):
    pass


class EmptySqueueError(TrailblazerError):
    pass


class TowerError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"TowerError: {self.message}"


class MissingSqueueOutput(TrailblazerError):
    """Raised when squeue results sre missing."""


class ValidationError(TrailblazerError):
    """
    Exception related to validations.
    """


class SlurmAPIClientError(TrailblazerError):
    """
    Exception related to Slurm API client.
    """


class InvalidSlurmResponseError(SlurmAPIClientError):
    """
    Exception related to the data in a  Slurm API client response.
    """


class SlurmRequestFailed(SlurmAPIClientError):
    """
    Exception raised when the Slurm API request fails.
    """


class TowerAPIClientError(TrailblazerError):
    """
    Exception related to Tower API client.
    """


class InvalidTowerAPIResponse(TowerAPIClientError):
    """
    Exception raised when the Tower API response is not formatted as expected.
    """


class TowerRequestFailed(TowerAPIClientError):
    """
    Exception raised when the Tower API request fails.
    """


class AnalysisServiceError(TrailblazerError):
    """
    Exception related to Analysis Service.
    """


class JobServiceError(TrailblazerError):
    pass


class NoJobsError(JobServiceError):
    pass


class SlurmAPIServiceError(TrailblazerError):
    pass


class SlurmCLIServiceError(TrailblazerError):
    pass


class TowerServiceError(TrailblazerError):
    pass


class TowerWorkflowIdFileMissing(TowerServiceError):
    pass
