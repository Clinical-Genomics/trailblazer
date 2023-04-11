# -*- coding: utf-8 -*-
import datetime as dt
from typing import List

import pytest

from tests.store.utils.conftest import JOB_LIST_PENDING


@pytest.fixture(name="timestamp_now")
def fixture_timestamp_now() -> dt.datetime:
    """Return a time stamp of today's date in date time format."""
    return dt.datetime.now()


@pytest.fixture(name="jobs_list")
def fixture_jobs_list() -> List[dict]:
    """Return a list of Tower Jobs."""
    return JOB_LIST_PENDING


@pytest.fixture(name="tower_case_id")
def fixture_tower_case_id() -> str:
    """Return a tower case ID."""
    return "cuddlyhen"
