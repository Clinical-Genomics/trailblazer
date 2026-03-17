from sqlalchemy import inspect

from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerPriority, TrailblazerTypes
from trailblazer.dto.create_analysis_request import CreateAnalysisRequest
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Analysis, User


def test_add_user(store: MockStore, user_email: str, username: str):
    """Test adding a user to the database."""
    # GIVEN an empty database
    assert not store.get_query(table=User).first()

    # WHEN adding a new user
    new_user: User = store.add_user(name=username, email=user_email, abbreviation="abb")

    # THEN it should be stored in the database
    user: User = apply_user_filter(
        filter_functions=[UserFilter.BY_EMAIL],
        users=store.get_query(table=User),
        email=user_email,
    ).first()
    assert new_user
    assert user == new_user


def test_add_pending_analysis(store: MockStore):
    # GIVEN a valid CreateAnalysisRequest
    analysis_data = CreateAnalysisRequest(
        case_id="pending_analysis_case_id",
        out_dir="/out/dir",
        priority=TrailblazerPriority.LOW,
        type=TrailblazerTypes.WGS,
    )

    # WHEN creating and storing a pending analysis
    analysis: Analysis = store.add_pending_analysis(analysis_data)

    # THEN an analysis has been created and persisted to the database
    assert inspect(analysis).persistent
