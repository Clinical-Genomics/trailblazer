from typing import Callable, List, Dict, Union, Optional

from trailblazer.store.base import BaseHandler_2
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import User


class ReadHandler(BaseHandler_2):
    """Class for reading items in the database."""

    def get_users(
        self,
        name: str = None,
        email: str = None,
        exclude_archived: bool = True,
    ) -> List[User]:
        """Return users from the database."""
        filter_map: Dict[Callable, Optional[Union[str, bool]]] = {
            UserFilter.FILTER_BY_CONTAINS_EMAIL: email,
            UserFilter.FILTER_BY_CONTAINS_NAME: name,
            UserFilter.FILTER_BY_IS_NOT_ARCHIVED: exclude_archived,
        }
        filter_functions: List[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        return apply_user_filter(
            filter_functions=filter_functions,
            users=self.get_query(table=User),
            email=email,
            name=name,
        ).all()
