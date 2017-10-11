# -*- coding: utf-8 -*-
from flask import url_for


def test_info_without_token(client):
    # GIVEN a server
    # WHEN accesssing the info API endpoint
    resp = client.get(url_for('api.info'))
    # THEN it should refuse access without JWT
    assert resp.status_code == 403
