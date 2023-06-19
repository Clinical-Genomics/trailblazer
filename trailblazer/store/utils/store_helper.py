"""Utility functions to simply add test data in a Trailblazer store."""
from trailblazer.store.api import Store
from trailblazer.store.models import Info, User


class StoreHelpers:
    """Class to hold helper functions that needs to be used all over."""

    @staticmethod
    def add_info(store: Store) -> Info:
        """Addd an info object to the store."""
        info: Info = Info()
        store.add(info)
        store.commit()
        return info

    @staticmethod
    def add_user(email: str, name: str, store: Store) -> User:
        """Addd a user object to the store."""
        user: User = User(email=email, name=name)
        store.add(user)
        store.commit()
        return user
