# -*- coding: utf-8 -*-
from trailblazer.store import models


def test_user_first_name():
    # GIVEN a user with a name
    user_obj = models.User(name='Paul T. Anderson')
    # WHEN accessing the first name
    first_name = user_obj.first_name
    # THEN it should return the spoken name
    assert first_name == 'Paul'
