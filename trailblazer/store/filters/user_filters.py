from enum import Enum
from typing import Callable, List, Optional

from sqlalchemy.orm import Query

from trailblazer.store.models import User


def filter_users_by_email(users: Query, email: str, **kwargs) -> Query:
    """Filter users with matching email."""
    return users.filter(User.email == email)


class UserFilter(Enum):
    """Define User filter functions."""

    FILTER_BY_EMAIL: Callable = filter_users_by_email


def apply_user_filter(
    users: Query,
    filter_functions: List[Callable],
    email: Optional[str] = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for function in filter_functions:
        users: Query = function(
            users=users,
            email=email,
        )
    return users
