# -*- coding: utf-8 -*-
from analysis import utils


def test_convert_job():
    # GIVEN a row from Sacct output
    row = ['666784', 'ChanjoSexCheck_ADM1657A7', 'prod001', 'core', '1',
           '01:47.603', '00:02:16', '2016-08-03T08:38:36',
           '2016-08-03T08:40:52', 'COMPLETED', '0:0']
    # WHEN parsing data out of it
    data = utils.convert_job(row)
    # THEN it should return more structured
    assert data['id'] == row[0]
    assert data['name'] == row[1]
