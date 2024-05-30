class TrailblazerError(Exception):
    pass


class JobServiceError(TrailblazerError):
    pass


class NoJobsError(JobServiceError):
    pass
