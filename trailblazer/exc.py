class TrailblazerError(Exception):
    def __init__(self, message):
        self.message = message


class MissingFileError(TrailblazerError):
    pass
