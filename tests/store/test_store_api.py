# -*- coding: utf-8 -*-
import datetime

import pytest


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
    store.track_update()
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
        ("crazygoat", True),  # running
        ("nicemouse", False),  # completed
        ("politesnake", False),  # failed
        ("gentlebird", True),  # pending
    ],
)
def test_is_latest_analysis_ongoing(sample_store, family, expected_bool):
    # GIVEN an analysis
    analysis_objs = sample_store.analyses(family=family).first()
    assert analysis_objs is not None
    # WHEN checking if the family has an ongoing analysis status
    is_ongoing = sample_store.is_latest_analysis_ongoing(family)
    # THEN it should return the expected result
    assert is_ongoing is expected_bool


@pytest.mark.parametrize(
    "family, expected_bool",
    [
        ("crazygoat", False),  # running
        ("nicemouse", False),  # completed
        ("politesnake", True),  # failed
        ("gentlebird", False),  # pending
    ],
)
def test_is_latest_analysis_failed(sample_store, family, expected_bool):
    # GIVEN an analysis
    analysis_objs = sample_store.analyses(family=family).first()
    assert analysis_objs is not None
    # WHEN checking if the family has a failed analysis status
    is_failed = sample_store.is_latest_analysis_failed(family)
    # THEN it should return the expected result
    assert is_failed is expected_bool


@pytest.mark.parametrize(
    "family, expected_bool",
    [
        ("crazygoat", False),  # running
        ("nicemouse", True),  # completed
        ("politesnake", False),  # failed
        ("gentlebird", False),  # pending
    ],
)
def test_is_latest_analysis_completed(sample_store, family, expected_bool):
    # GIVEN an analysis
    analysis_objs = sample_store.analyses(family=family).first()
    assert analysis_objs is not None
    # WHEN checking if the family has a failed analysis status
    is_failed = sample_store.is_latest_analysis_completed(family)
    # THEN it should return the expected result
    assert is_failed is expected_bool


@pytest.mark.parametrize(
    "family, expected_status",
    [
        ("crazygoat", "running"),
        ("nicemouse", "completed"),
        ("politesnake", "failed"),
        ("gentlebird", "pending"),
    ],
)
def test_get_latest_analysis_status(sample_store, family, expected_status):
    # GIVEN an analysis
    analysis_objs = sample_store.analyses(family=family).first()
    assert analysis_objs is not None
    # WHEN checking if the family has an analysis status
    status = sample_store.get_latest_analysis_status(family)
    # THEN it should return the expected result
    assert status is expected_status


def test_aggregate_jobs(sample_store):

    # GIVEN a store with some analyses
    assert sample_store.analyses().count() > 0
    all_jobs = sample_store.jobs().count()
    assert all_jobs == 2

    # WHEN aggregating data on failed jobs
    jobs_data = sample_store.aggregate_failed()

    # THEN it should return a list of dicts per job type with count
    assert isinstance(jobs_data, list)

    # ... it should exclude "cancelled" jobs
    assert len(jobs_data) == 1
    assert jobs_data[0]["name"] == "samtools_mpileup"
    assert jobs_data[0]["count"] == 1


def test_aggregate_jobs_since_forever_date(sample_store):

    # GIVEN a store with some analyses
    assert sample_store.analyses().count() > 0
    all_jobs = sample_store.jobs().count()
    assert all_jobs == 2
    # a date a gazillion days back
    date_since = datetime.datetime.now() - datetime.timedelta(days=9999)

    # WHEN aggregating data on failed jobs
    jobs_data = sample_store.aggregate_failed(date_since)

    # THEN it should return a list of dicts per job type with count
    assert len(jobs_data) == 1
    assert jobs_data[0]["name"] == "samtools_mpileup"
    assert jobs_data[0]["count"] == 1


def test_aggregate_jobs_since_yesterday(sample_store):

    # GIVEN a store with some analyses
    assert sample_store.analyses().count() > 0
    all_jobs = sample_store.jobs().count()
    assert all_jobs == 2
    # a date a gazillion days back
    date_since = datetime.datetime.now() - datetime.timedelta(days=1)

    # WHEN aggregating data on failed jobs
    jobs_data = sample_store.aggregate_failed(date_since)

    # THEN it should return a list of dicts per job type with count
    assert len(jobs_data) == 0
