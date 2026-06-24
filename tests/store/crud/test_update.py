from datetime import datetime

from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.dto.update_analyses import AnalysisUpdate, UpdateAnalyses
from trailblazer.store.database import get_session
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Analysis, Delivery, User
from trailblazer.store.store import Store


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


def test_update_analysis_hold_delivery(analysis_store: MockStore, case_id: str):
    # GIVEN an analysis which is not visible
    # TODO: Complete this test
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id)
    analysis.is_visible = False

    # WHEN making the analysis visible
    analysis_store.update_analysis(analysis_id=analysis.id, is_visible=True)

    # THEN the analysis should be visible
    assert analysis.is_visible


def test_update_analysis_is_delivered(
    analysis_store: MockStore, case_id: str, mocker: MockerFixture
):
    # GIVEN an analysis which has not been delivered
    session: Session = get_session()
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id)

    # GIVEN a valid user
    user = User(
        id=1,
        abbreviation="CG",
        email="some_mail@some_domain",
    )
    commit_spy = mocker.spy(session, "commit")

    # WHEN updating the analysis to be delivered
    analysis_store.update_analysis(analysis_id=analysis.id, is_delivered=True, user=user)

    # THEN the analysis should have a delivery entry
    assert analysis.delivery

    # THEN the change should not have been committed
    commit_spy.assert_not_called()


def test_update_deliver_analysis_success(store: Store, mocker: MockerFixture):
    # GIVEN an analysis in the database that has not been delivered
    session: Session = get_session()
    analysis = Analysis(
        id=1,
        case_id="test_case",
        status=TrailblazerStatus.COMPLETED,
        logged_at=datetime.now(),
        version="1.0",
        workflow_manager="nf_tower",
    )

    # GIVEN a valid user
    user = User(
        id=1,
        abbreviation="CG",
        email="some_mail@some_domain",
    )

    session.add(analysis)
    session.add(user)
    session.commit()
    commit_spy = mocker.spy(session, "commit")

    # WHEN calling update_analysis_delivery with is_delivered=True
    store.update_analysis_delivery(analysis=analysis, is_delivered=True, user=user)

    # THEN the analysis should have an associated delivery entry
    assert analysis.delivery

    # THEN the change should not have been committed
    commit_spy.assert_not_called()


def test_update_undeliver_analysis_success(store: Store, mocker: MockerFixture):
    # GIVEN an analysis in the database that has been delivered
    session: Session = get_session()
    analysis = Analysis(
        id=1,
        case_id="test_case",
        status=TrailblazerStatus.COMPLETED,
        logged_at=datetime.now(),
        version="1.0",
        workflow_manager="nf_tower",
    )
    delivery = Delivery(analysis_id=1, delivered_by=1, delivered_date=datetime.now())

    # GIVEN a valid user
    user = User(
        id=1,
        abbreviation="CG",
        email="some_mail@some_domain",
    )

    session.add(analysis)
    session.add(user)
    session.add(delivery)
    session.commit()
    commit_spy = mocker.spy(session, "commit")

    # WHEN calling update_analysis_delivery with is_delivered=False
    store.update_analysis_delivery(analysis=analysis, is_delivered=False, user=user)

    # THEN the analysis should not have an associated delivery entry
    assert analysis.delivery in session.deleted

    # THEN the change should not have been committed
    commit_spy.assert_not_called()


def test_update_analyses(store: Store, mocker: MockerFixture):
    # GIVEN a store with two analyses
    analysis_1 = Analysis(
        id=1, case_id="updog", comment="", is_visible=False, status=TrailblazerStatus.FAILED
    )
    analysis_2 = Analysis(
        id=2, case_id="badbunny", comment="", is_visible=False, status=TrailblazerStatus.PENDING
    )

    session = get_session()
    commit_call = mocker.spy(session, "commit")
    session.add_all([analysis_1, analysis_2])

    analysis_update_1 = AnalysisUpdate(
        id=1,
        comment="hey (horse)",
        is_visible=True,
        status=TrailblazerStatus.COMPLETED,
    )
    analysis_update_2 = AnalysisUpdate(
        id=2,
        comment="hey (cow)",
        is_visible=True,
        status=TrailblazerStatus.COMPLETED,
    )

    update_analyses = UpdateAnalyses(analyses=[analysis_update_1, analysis_update_2])

    # WHEN updating analyses
    store.update_analyses(data=update_analyses)

    # THEN the analyses should have been updated
    assert analysis_1.comment == "hey (horse)"
    assert analysis_1.is_visible is True
    assert analysis_1.status is TrailblazerStatus.COMPLETED

    assert analysis_2.comment == "hey (cow)"
    assert analysis_2.is_visible is True
    assert analysis_2.status is TrailblazerStatus.COMPLETED

    # THEN the changes should not have been committed
    commit_call.assert_not_called()
