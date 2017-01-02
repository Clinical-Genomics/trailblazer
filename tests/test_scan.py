# -*- coding: utf-8 -*-
from trailblazer import scan


def test_scan_dir():
    # GIVEN a customer dir with one analysis
    root_dir = 'tests/fixtures/mip4/cust000'
    # WHEN looking for included analyses
    files = scan.scan_dir(root_dir)
    # THEN it should return a list with one file
    assert len(files) == 1
