class TrailblazerError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"TrailblazerError: {self.message}"


class MissingFileError(TrailblazerError):
    pass


class EmptySqueueError(TrailblazerError):
    pass
