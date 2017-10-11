# -*- coding: utf-8 -*-


class TrailblazerError(Exception):

    def __init__(self, message):
        self.message = message


class MissingFileError(TrailblazerError):
    pass


class MipStartError(TrailblazerError):
    pass


class ConfigError(TrailblazerError):

    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
