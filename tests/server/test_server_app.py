# -*- coding: utf-8 -*-
from flask import url_for


def test_index(client):
    # GIVEN a server
    # WHEN accessing the public index page
    resp = client.get(url_for('index'))
    # THEN it should be ok
    assert resp.status_code == 200
