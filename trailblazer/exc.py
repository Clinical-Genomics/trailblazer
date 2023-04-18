class TrailblazerError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"TrailblazerError: {self.message}"


class MissingFileError(TrailblazerError):
    pass


class EmptySqueueError(TrailblazerError):
    pass


class TowerError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"TowerError: {self.message}"


class TowerRequirementsError(TowerError):
    """Raised when Tower requirements are not satisfied."""


class TowerResponseError(TowerError):
    """Raised when an invalid Tower response is returned."""
