# -*- coding: utf-8 -*-


class TrailblazerError(Exception):
    def __init__(self, message):
        self.message = message


class MissingFileError(TrailblazerError):
    pass


class MipStartError(TrailblazerError):
    pass


class ConfigError(TrailblazerError):
    pass
