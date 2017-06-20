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
