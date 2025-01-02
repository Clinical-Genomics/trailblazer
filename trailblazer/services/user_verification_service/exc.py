from trailblazer.exc import TrailblazerError


class UserTokenVerificationError(TrailblazerError):
    pass


class InvalidTokenError(UserTokenVerificationError):
    pass


class ExpiredTokenError(UserTokenVerificationError):
    pass
