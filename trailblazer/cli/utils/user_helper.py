import logging

from trailblazer.store.models import User

LOG = logging.getLogger(__name__)


def is_existing_user(user: User, email: str) -> bool:
    """Check if supplied user exist in db."""
    if not user:
        LOG.error(f"User with email {email} not found")
        return False
    return True


def is_user_archived(user: User, email: str) -> bool:
    """Check if user is archived."""
    LOG.error(f"User with email {email} has archive status: {user.is_archived}")
    return user.is_archived
