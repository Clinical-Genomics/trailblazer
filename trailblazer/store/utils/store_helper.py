"""Utility functions to simply add test data in a Trailblazer store."""
from trailblazer.store.api import Store
from trailblazer.store.models import Info


class StoreHelpers:
    """Class to hold helper functions that needs to be used all over."""

    @staticmethod
    def add_info(store: Store) -> Info:
        """Addd an info object to the store."""
        info: Info = Info()
        store.add(info)
        store.commit()
        return info
