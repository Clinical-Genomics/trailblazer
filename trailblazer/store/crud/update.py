from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import User


class UpdateHandler(BaseHandler_2):
    """Class for updating items in the database."""

    def add_user(self, name: str, email: str) -> User:
        """Add a new user to the database."""
        new_user: User = self.User(email=email, name=name)
        self.add_commit(new_user)
        return new_user
