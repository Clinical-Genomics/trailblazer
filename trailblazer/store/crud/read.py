from trailblazer.store.base import BaseHandler_2
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import User


class ReadHandler(BaseHandler_2):
    """Class for reading items in the database."""

    def get_users(
        self,
        name: str = None,
        email: str = None,
        include_archived: bool = False,
    ) -> User:
        """Return all users from the database."""
        filter_map = {
            UserFilter.FILTER_BY_EMAIL: email,
            UserFilter.FILTER_BY_IS_ARCHIVED: include_archived,
            UserFilter.FILTER_BY_NAME: name,
        }
        filter_functions: list = []
        for function, supplied_arg in filter_map.items():
            if supplied_arg:
                filter_functions.append(function)
        return apply_user_filter(
            filter_functions=filter_functions,
            users=self.get_query(table=User),
            email=email,
            name=name,
        ).all()
