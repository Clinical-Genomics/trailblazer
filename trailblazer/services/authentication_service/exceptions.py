class AuthenticationError(Exception):
    pass


class UserNotFoundError(AuthenticationError):
    pass
