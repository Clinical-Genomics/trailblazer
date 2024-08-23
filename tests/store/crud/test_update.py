from datetime import datetime
from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Analysis, User


def test_update_analysis_jobs(analysis_store: MockStore, tower_jobs: list[dict], case_id: str):
    """Test jobs are successfully updated."""

    # GIVEN an analysis with no jobs
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert not analysis.jobs

    # WHEN jobs are updated
    analysis_store.update_jobs(jobs=tower_jobs[:2])

    # THEN there should be jobs
    assert analysis.jobs


def test_update_user_is_archived(user_store: MockStore, user_email: str):
    """Test updating user is archived attribute."""
    # GIVE a database and a not archived user
    user: User = apply_user_filter(
        filter_functions=[UserFilter.BY_EMAIL],
        users=user_store.get_query(table=User),
        email=user_email,
    ).first()
    assert not user.is_archived

    # WHEN updating a user archive status
    user_store.update_user_is_archived(user=user, archive=True)

    archived_user: User = apply_user_filter(
        filter_functions=[UserFilter.BY_EMAIL],
        users=user_store.get_query(table=User),
        email=user_email,
    ).first()

    # THEN user should be recorded as archived in the database
    assert archived_user


def test_update_analysis_status_with_failed(analysis_store: MockStore, case_id: str):
    """Test setting analysis to failed for an analysis."""

    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status != TrailblazerStatus.FAILED

    # WHEN setting analysis to failed
    analysis_store.update_analysis_status_by_case_id(
        case_id=analysis.case_id, status=TrailblazerStatus.FAILED
    )

    # THEN the analysis status should be updated to failed
    assert analysis.status == TrailblazerStatus.FAILED


def test_update_analysis_status_to_completed(analysis_store: MockStore, case_id: str):
    """Test setting analysis to completed for an analysis."""

    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status != TrailblazerStatus.COMPLETED

    # WHEN setting analysis to completed
    analysis_store.update_analysis_status_to_completed(analysis_id=analysis.id)

    # THEN the analysis status should be updated to completed
    assert analysis.status == TrailblazerStatus.COMPLETED


def test_update_analysis_uploaded_at(
    analysis_store: MockStore, timestamp_now: datetime, case_id: str
):
    """Test setting analysis uploaded at for an analysis."""
    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)

    # WHEN setting an analysis uploaded at
    analysis_store.update_analysis_uploaded_at(case_id=analysis.case_id, uploaded_at=timestamp_now)

    # THEN uploaded at should be updated
    assert analysis.uploaded_at == timestamp_now


def test_update_analysis_comment(analysis_store: MockStore, case_id: str):
    """Test adding comment to an analysis."""

    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    comment: str = "test comment"

    # WHEN adding a comment
    analysis_store.update_latest_analysis_comment(case_id=analysis.case_id, comment=comment)

    # THEN a comment should have been added
    assert analysis.comment == comment


def test_update_analysis_comment_when_existing(analysis_store: MockStore, case_id: str):
    """Test adding comment to an analysis when a comment already exists."""

    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    first_comment: str = "One"
    second_comment: str = "Second"

    # WHEN adding a comment
    analysis_store.update_latest_analysis_comment(case_id=analysis.case_id, comment=first_comment)
    analysis_store.update_latest_analysis_comment(case_id=analysis.case_id, comment=second_comment)

    # THEN comments should have been added
    assert analysis.comment == f"{first_comment} {second_comment}"


def test_update_tower_jobs(analysis_store: MockStore, tower_jobs: list[dict], case_id: str):
    """Assess that jobs are successfully updated when using NF Tower."""

    # GIVEN an analysis without jobs
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)

    # WHEN analysis jobs are deleted
    analysis_store.delete_analysis_jobs(analysis=analysis)

    # THEN the analysis object should have no jobs
    assert not analysis.jobs

    # WHEN jobs are updated
    analysis_store.update_jobs(jobs=tower_jobs[:2])

    # THEN jobs should be updated
    assert len(analysis.jobs) == 2


def test_update_analysis_with_comment(analysis_store: MockStore, case_id: str):
    # GIVEN an analysis without a comment
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id)
    analysis.comment = ""

    # WHEN updating the analysis with a comment
    analysis_store.update_analysis(analysis_id=analysis.id, comment="test")

    # THEN the comment should be set
    assert analysis.comment == "test"


def test_update_analysis_status(analysis_store: MockStore, case_id: str):
    # GIVEN an analysis with a non failed status
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id)
    assert analysis.status != "failed"

    # WHEN giving the analysis a status
    analysis_store.update_analysis(analysis_id=analysis.id, status="failed")

    # THEN the status should be set
    assert analysis.status == "failed"


def test_update_analysis_visibility(analysis_store: MockStore, case_id: str):
    # GIVEN an analysis which is not visible
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id)
    analysis.is_visible = False

    # WHEN making the analysis visible
    analysis_store.update_analysis(analysis_id=analysis.id, is_visible=True)

    # THEN the analysis should be visible
    assert analysis.is_visible
