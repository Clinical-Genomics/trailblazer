from datetime import datetime
from typing import List, Dict, Union

from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.models import User, Analysis
from tests.store.utils.store_helper import StoreHelpers


def test_get_analysis_with_id(analysis_store: MockStore):
    """Test getting an analysis when it exists in the database."""
    # GIVEN a store with an analysis
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN accessing it by ID
    analysis: Analysis = analysis_store.get_analysis_with_id(analysis_id=existing_analysis.id)

    # THEN it should return the same analysis
    assert analysis == existing_analysis


def test_get_analysis_with_id_when_missing(analysis_store: MockStore):
    """Test getting an analysis when it does not exist in the database."""
    # GIVEN an id that doesn't exist
    missing_analysis_id = 12312423534

    # WHEN accessing the analysis
    analysis: Analysis = analysis_store.get_analysis_with_id(analysis_id=missing_analysis_id)

    # THEN it should return None
    assert not analysis


def test_get_nr_jobs_with_status_per_category(job_store: MockStore, timestamp_yesterday: datetime):
    """Test getting the number of failed jobs per category since a supplied date from the database."""
    # GIVEN a database with jobs

    # WHEN querying for failed users
    failed_jobs: List[Dict[str, Union[str, int]]] = job_store.get_nr_jobs_with_status_per_category(
        since_when=timestamp_yesterday, status=TrailblazerStatus.FAILED
    )

    # THEN failed jobs should be returned
    assert failed_jobs

    # THEN one job should be returned
    assert len(failed_jobs) == 1

    # THEN name and count should be defined
    assert failed_jobs[0].get("name") == "1"
    assert failed_jobs[0].get("count") == 1


def test_get_user(user_store: MockStore, user_email: str):
    """Test getting a user from the database."""
    # GIVEN a database with a user

    # WHEN querying for a user
    user: User = user_store.get_user(email=user_email)

    # THEN it should be returned
    assert user.email == user_email


def test_get_user_including_archived(user_store: MockStore, archived_user_email: str):
    """Test getting an archived user from the database."""
    # GIVEN a database with an archived user

    # WHEN querying for a user
    user: User = user_store.get_user(email=archived_user_email, exclude_archived=False)

    # THEN it should be returned
    assert user.email == archived_user_email


def test_get_user_including_archive_false(user_store: MockStore, archived_user_email: str):
    """Test getting an archived user from the database."""
    # GIVEN a database with an archived user

    # WHEN querying for a user
    user: User = user_store.get_user(email=archived_user_email, exclude_archived=True)

    # THEN no user should be returned
    assert not user


def test_get_user_when_non_existing(user_store: MockStore):
    """Test getting a non-existing user from the database."""
    # GIVEN a database with a user

    # WHEN querying for a user that doesn't exist
    user: User = user_store.get_user(email="this_is_a_made_up_email@fake_example.com")

    # THEN it should return as None
    assert user is None


def test_get_users(user_store: MockStore, user_email: str, username: str):
    """Test getting a user with username and email."""
    # GIVEN a database with a user

    # WHEN getting users
    users: List[User] = user_store.get_users(name=username, email=user_email)

    # THEN the user should be returned
    assert users[0].email == user_email


def test_get_users_including_archived(user_store: MockStore, user_email: str, username: str):
    """Test getting a user with username and email which are archived."""
    # GIVEN a database with a user and an archived user
    StoreHelpers.add_user(
        name=username, email="old.user@magnolia.com", store=user_store, is_archived=True
    )

    # WHEN getting users
    users: List[User] = user_store.get_users(name=username, exclude_archived=False)

    # THEN the two users should be returned
    assert len(users) == 2


def test_get_users_no_username(user_store: MockStore, user_email: str):
    """Test getting a user by email."""
    # GIVEN a database with a user

    # WHEN getting users
    users: List[User] = user_store.get_users(email=user_email)

    # THEN the user should be returned
    assert users[0].email == user_email
