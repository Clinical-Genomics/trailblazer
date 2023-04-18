import datetime
from typing import List

import pytest

from tests.apps.tower.conftest import CaseIDs
from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.models import Analysis


def test_setup_and_info(store):
    # GIVEN a store which is already setup
    assert len(store.engine.table_names()) > 0

    # THEN it should contain an Info entry with a default "created_at" date
    info_obj = store.info()
    assert isinstance(info_obj.created_at, datetime.datetime)


def test_track_update(store):
    # GIVEN a store which is empty apart from the initialized info entry
    assert store.info().updated_at is None

    # WHEN updating the last updated date
    store.set_latest_update_date()

    # THEN it should update info entry with the current date
    assert isinstance(store.info().updated_at, datetime.datetime)


def test_add_user(store):
    # GIVEN an empty database
    assert store.User.query.first() is None
    name, email = "Paul T. Anderson", "paul.anderson@magnolia.com"

    # WHEN adding a new user
    new_user = store.add_user(name, email)

    # THEN it should be stored in the database
    assert store.User.query.filter_by(email=email).first() == new_user


def test_user(store):
    # GIVEN a database with a user
    name, email = "Paul T. Anderson", "paul.anderson@magnolia.com"
    store.add_user(name, email)
    assert store.User.query.filter_by(email=email).first().email == email

    # WHEN querying for a user
    user_obj = store.user(email)

    # THEN it should be returned
    assert user_obj.email == email

    # WHEN querying for a user that doesn't exist
    user_obj = store.user("this_is_a_made_up_email@fake_example.com")

    # THEN it should return as None
    assert user_obj is None


def test_analysis(sample_store):
    # GIVEN a store with an analysis
    existing_analysis = sample_store.analyses().first()

    # WHEN accessing it by ID
    analysis_obj = sample_store.analysis(existing_analysis.id)

    # THEN it should return the same analysis
    assert analysis_obj == existing_analysis

    # GIVEN an id that doesn't exist
    missing_analysis_id = 12312423534

    # WHEN accessing the analysis
    analysis_obj = sample_store.analysis(missing_analysis_id)

    # THEN it should return None
    assert analysis_obj is None


@pytest.mark.parametrize(
    "family, expected_bool",
    [
        ("blazinginsect", True),  # running
        ("nicemice", False),  # completed
        ("lateraligator", False),  # failed
        ("escapedgoat", True),  # pending
    ],
)
def test_is_latest_analysis_ongoing(sample_store, family: str, expected_bool: bool):
    # GIVEN an analysis
    sample_store.update_ongoing_analyses()
    analysis_objs = sample_store.analyses(case_id=family).first()
    assert analysis_objs is not None

    # WHEN checking if the family has an ongoing analysis status
    is_ongoing = sample_store.is_latest_analysis_ongoing(case_id=family)

    # THEN it should return the expected result
    assert is_ongoing is expected_bool


def test_set_analysis_uploaded(sample_store, timestamp_now: datetime):
    """Test setting analysis uploaded at for an analysis."""

    # GIVEN a store with an analysis
    analysis_obj: Analysis = sample_store.analyses().first()
    uploaded_at: datetime = timestamp_now

    # WHEN setting an analysis uploaded at
    sample_store.set_analysis_uploaded(case_id=analysis_obj.family, uploaded_at=uploaded_at)

    # THEN the column uploaded_at should be updated
    assert analysis_obj.uploaded_at == uploaded_at


def test_set_analysis_failed(sample_store):
    """Test setting analysis to failed for an analysis."""

    # GIVEN a store with an analysis
    analysis_obj: Analysis = sample_store.analyses().first()

    # WHEN setting analysis to failed
    sample_store.set_analysis_status(case_id=analysis_obj.family, status="failed")

    # THEN the column status should be updated with failed.
    assert analysis_obj.status == "failed"


def test_add_comment(sample_store):
    """Test adding comment to an analysis object."""

    # GIVEN a store with an analysis
    analysis_obj: Analysis = sample_store.analyses().first()
    comment: str = "test comment"

    # WHEN adding a comment
    sample_store.add_comment(case_id=analysis_obj.family, comment=comment)

    # THEN a comment should have been added
    assert analysis_obj.comment == comment


@pytest.mark.parametrize(
    "family, expected_bool",
    [
        ("blazinginsect", False),  # running
        ("nicemice", False),  # completed
        ("lateraligator", True),  # failed
        ("escapedgoat", False),  # pending
    ],
)
def test_is_latest_analysis_failed(sample_store, family: str, expected_bool: bool):
    # GIVEN an analysis
    sample_store.update_ongoing_analyses()
    analysis_objs = sample_store.analyses(case_id=family).first()
    assert analysis_objs is not None

    # WHEN checking if the family has a failed analysis status
    is_failed = sample_store.is_latest_analysis_failed(case_id=family)

    # THEN it should return the expected result
    assert is_failed is expected_bool


@pytest.mark.parametrize(
    "family, expected_bool",
    [
        ("blazinginsect", False),  # running
        ("nicemice", True),  # completed
        ("lateraligator", False),  # failed
        ("escapedgoat", False),  # pending
    ],
)
def test_is_latest_analysis_completed(sample_store, family: str, expected_bool: bool):
    # GIVEN an analysis
    sample_store.update_ongoing_analyses()
    analysis_objs = sample_store.analyses(case_id=family).first()
    assert analysis_objs is not None

    # WHEN checking if the family has a failed analysis status
    is_failed = sample_store.is_latest_analysis_completed(case_id=family)

    # THEN it should return the expected result
    assert is_failed is expected_bool


@pytest.mark.parametrize(
    "family, expected_status",
    [
        ("blazinginsect", "running"),  # running
        ("nicemice", "completed"),  # completed
        ("lateraligator", "failed"),  # failed
        ("escapedgoat", "pending"),  # pending
    ],
)
def test_get_latest_analysis_status(sample_store, family: str, expected_status: str):
    # GIVEN an analysis
    sample_store.update_ongoing_analyses()
    analysis_objs = sample_store.analyses(case_id=family).first()
    assert analysis_objs is not None

    # WHEN checking if the family has an analysis status
    status = sample_store.get_latest_analysis_status(case_id=family)

    # THEN it should return the expected result
    assert status is expected_status


@pytest.mark.parametrize(
    "case_id, status",
    [
        ("blazinginsect", "running"),
        ("crackpanda", "failed"),
        ("daringpidgeon", "error"),
        ("emptydinosaur", "error"),
        ("escapedgoat", "pending"),
        ("fancymole", "completed"),
        ("happycow", "pending"),
        ("lateraligator", "failed"),
        ("liberatedunicorn", "error"),
        ("nicemice", "completed"),
        ("rarekitten", "canceled"),
        ("trueferret", "running"),
    ],
)
def test_update(sample_store, case_id, status):
    # GIVEN an analysis
    analysis_obj = sample_store.get_latest_analysis(case_id)

    # WHEN database is updated once
    sample_store.update_run_status(analysis_obj.id)

    # THEN analysis status is changed to what is expected
    assert analysis_obj.status == status

    # WHEN database is updated a second time
    sample_store.update_run_status(analysis_obj.id)

    # THEN the status is still what is expected, and no database errors were raised
    assert analysis_obj.status == status


def test_mark_analyses_deleted(sample_store):
    # GIVEN case_id for a case that is not deleted
    case_id = "liberatedunicorn"
    analysis_obj = sample_store.get_latest_analysis(case_id)
    assert not analysis_obj.is_deleted

    # WHEN running command
    sample_store.mark_analyses_deleted(case_id=case_id)
    analysis_obj = sample_store.get_latest_analysis(case_id)

    # THEN analysis is marked deleted
    assert analysis_obj.is_deleted


def test_update_tower_jobs(sample_store: MockStore, tower_jobs: List[dict], case_id: str):
    """Assess that jobs are successfully updated when using NF Tower."""

    # GIVEN an analysis without failed jobs
    analysis: Analysis = sample_store.get_latest_analysis(case_id=case_id)
    assert not analysis.failed_jobs

    # WHEN jobs are updated
    sample_store.update_jobs(analysis=analysis, jobs=tower_jobs)

    # THEN analysis object should have failed jobs
    assert len(analysis.failed_jobs) == 3

    # WHEN jobs are updated a second time
    sample_store.update_jobs(analysis=analysis, jobs=tower_jobs[:2])

    # THEN failed jobs should be updated
    assert len(analysis.failed_jobs) == 2


@pytest.mark.parametrize(
    "case_id, status, progress",
    [
        (CaseIDs.RUNNING, TrailblazerStatus.RUNNING.value, 15),
        (CaseIDs.PENDING, TrailblazerStatus.PENDING.value, 0),
        (CaseIDs.COMPLETED, TrailblazerStatus.COMPLETED.value, 100),
    ],
)
def test_update_tower_run_status(sample_store: MockStore, case_id: str, status: str, progress: int):
    """Assess that an analysis status is successfully updated when using NF Tower."""

    # GIVEN an analysis with pending status
    analysis: Analysis = sample_store.get_latest_analysis(case_id=case_id)
    assert analysis.status == TrailblazerStatus.PENDING.value

    # WHEN database is updated once
    sample_store.update_run_status(analysis_id=analysis.id)

    # THEN analysis status is changed to what is expected
    assert analysis.status == status
    assert analysis.progress == progress

    # WHEN database is updated a second time
    sample_store.update_run_status(analysis_id=analysis.id)

    # THEN the status is still as before, and no database errors were raised
    assert analysis.status == status
    assert analysis.progress == progress
