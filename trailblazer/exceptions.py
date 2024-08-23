class TrailblazerError(Exception):
    pass


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
