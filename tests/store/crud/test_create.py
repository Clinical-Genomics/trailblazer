from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Analysis, User


def test_add_pending_analysis(raw_analyses: list[dict], store: MockStore, user_email: str):
    """Test adding a new analysis to the database."""
    # GIVEN an empty database
    assert not store.get_query(table=Analysis).first()

    # GIVEN an unprocessed raw analysis
    analysis: dict = raw_analyses[0]

    # WHEN adding a new analysis
    new_analysis: Analysis = store.add_pending_analysis(
        case_id=analysis.get("family"),
        config_path=analysis.get("config_path"),
        email=user_email,
        out_dir=analysis.get("out_dir"),
        priority=analysis.get("priority"),
        type=analysis.get("type"),
    )

    # THEN it should be stored in the database
    stored_analysis: Analysis = store.get_analysis(
        case_id=analysis.get("family"),
        started_at=new_analysis.started_at,
        status=analysis.get("status"),
    )
    assert new_analysis and stored_analysis
    assert stored_analysis == new_analysis


def test_add_user(store: MockStore, user_email: str, username: str):
    """Test adding a user to the database."""
    # GIVEN an empty database
    assert not store.get_query(table=User).first()

    # WHEN adding a new user
    new_user: User = store.add_user(name=username, email=user_email)

    # THEN it should be stored in the database
    user: User = apply_user_filter(
        filter_functions=[UserFilter.FILTER_BY_EMAIL],
        users=store.get_query(table=User),
        email=user_email,
    ).first()
    assert new_user
    assert user == new_user
