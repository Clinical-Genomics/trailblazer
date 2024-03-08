from enum import Enum
from typing import Callable

from sqlalchemy.orm import Query

from trailblazer.store.models import User


def filter_users_by_email(users: Query, email: str, **kwargs) -> Query:
    """Filter users with matching email."""
    return users.filter(User.email == email)


def filter_users_by_contains_email(users: Query, email: str, **kwargs) -> Query:
    """Filter users which contains email."""
    return users.filter(User.email.contains(email))


def filter_users_by_contains_name(users: Query, name: str, **kwargs) -> Query:
    """Filter users which contains name."""
    return users.filter(User.name.contains(name))


def filter_users_by_is_not_archived(users: Query, **kwargs) -> Query:
    """Filter users which are not archived."""
    return users.filter(User.is_archived.is_(False))


def filter_users_by_id(users: Query, id: int, **kwargs) -> Query:
    """Filter users by id."""
    return users.filter(User.id == id)


class UserFilter(Enum):
    """Define User filter functions."""

    BY_ID: Callable = filter_users_by_id
    BY_CONTAINS_EMAIL: Callable = filter_users_by_contains_email
    BY_CONTAINS_NAME: Callable = filter_users_by_contains_name
    BY_EMAIL: Callable = filter_users_by_email
    BY_IS_NOT_ARCHIVED: Callable = filter_users_by_is_not_archived


def apply_user_filter(
    users: Query,
    filter_functions: list[Callable],
    email: str | None = None,
    id: int | None = None,
    name: str | None = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for function in filter_functions:
        users: Query = function(
            users=users,
            email=email,
            id=id,
            name=name,
        )
    return users
