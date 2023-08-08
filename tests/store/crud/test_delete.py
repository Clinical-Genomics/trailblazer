from typing import List

from tests.mocks.store_mock import MockStore
from trailblazer.store.models import Analysis


def test_delete_analysis_jobs(analysis_store: MockStore, tower_jobs: List[dict], case_id: str):
    """Test jobs are successfully deleted."""

    # GIVEN an analysis without failed jobs
    analysis: Analysis = analysis_store.get_latest_analysis(case_id=case_id)
    assert not analysis.failed_jobs

    # WHEN jobs are updated
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

    assert analysis.failed_jobs

    # WHEN jobs are deleted
    analysis_store.delete_analysis_jobs(analysis=analysis)

    # THEN analysis object should have no jobs
    assert not analysis.failed_jobs