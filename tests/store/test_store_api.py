# -*- coding: utf-8 -*-
import datetime


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
    name, email = 'Paul T. Anderson', 'paul.anderson@magnolia.com'
    # WHEN adding a new user
    new_user = store.add_user(name, email)
    # THEN it should be stored in the database
    assert store.User.query.filter_by(email=email).first() == new_user


def test_user(store):
    # GIVEN a database with a user
    name, email = 'Paul T. Anderson', 'paul.anderson@magnolia.com'
    store.add_user(name, email)
    assert store.User.query.filter_by(email=email).first().email == email
    # WHEN querying for a user
    user_obj = store.user(email)
    # THEN it should be returned
    assert user_obj.email == email

    # WHEN querying for a user that doesn't exist
    user_obj = store.user('this_is_a_made_up_email@fake_example.com')
    # THEN it should return as None
    assert user_obj is None
