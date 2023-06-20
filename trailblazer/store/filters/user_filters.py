from enum import Enum
from typing import Callable, List, Optional

from sqlalchemy.orm import Query

from trailblazer.store.models import User


def filter_users_by_email(users: Query, email: str, **kwargs) -> Query:
    """Filter users with matching email."""
    return users.filter(User.email == email)


def filter_users_by_name(users: Query, name: str, **kwargs) -> Query:
    """Filter users with matching name."""
    return users.filter(User.name == name)


def filter_users_by_is_archived(users: Query, **kwargs) -> Query:
    """Filter archived users."""
    return users.filter_by(is_archived=False)


class UserFilter(Enum):
    """Define User filter functions."""

    FILTER_BY_EMAIL: Callable = filter_users_by_email
    FILTER_BY_IS_ARCHIVED: Callable = filter_users_by_is_archived
    FILTER_BY_NAME: Callable = filter_users_by_name


def apply_user_filter(
    users: Query,
    filter_functions: List[Callable],
    email: Optional[str] = None,
    name: Optional[str] = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for function in filter_functions:
        users: Query = function(
            users=users,
            email=email,
            name=name,
        )
    return users
