from unittest.mock import Mock, create_autospec

from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

import trailblazer.services.analysis_service.analysis_service as service
from trailblazer.constants import TrailblazerStatus
from trailblazer.dto.update_analyses import AnalysisUpdate, UpdateAnalyses
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.models import Analysis, User
from trailblazer.store.store import Store


def test_patch_analyses_delivered(  # TODO: Expand to include another analysis, autospec store
    # analysis_store: Store,
    analysis_id: int,
    analysis_service: AnalysisService,
    mocker: MockerFixture,
):
    # GIVEN a store with two analyses and a user
    store: Store = create_autospec(Store)
    analysis_1 = create_autospec(Analysis, id=1)
    analysis_2 = create_autospec(Analysis, id=2)
    store.update_analyses = Mock(return_value=[analysis_1, analysis_2])
    user = User(id=1)

    # GIVEN a store session
    session = create_autospec(Session)
    mocker.patch.object(service, "get_session", return_value=session)

    # GIVEN a request to mark an analysis as delivered
    analysis_update_1 = AnalysisUpdate(id=1, is_delivered=True)
    analysis_update_2 = AnalysisUpdate(id=2, is_delivered=True)
    update_analyses = UpdateAnalyses(analyses=[analysis_update_1, analysis_update_2])

    # WHEN updating the analysis
    analysis_service.update_analyses(data=update_analyses, user=user)

    # THEN the store method should have been called
    store.update_analyses.assert_called_once_with(data=update_analyses, user=user)

    # THEN the changes were persisted only once
    session.commit.assert_called_once()


# TODO: Test update_analyses with one analysis failing verifying that no commit is done

# TODO: Add test for update_analysis both happy path and failure.


def test_cancel_analysis(analysis_service: AnalysisService, analysis_with_running_jobs: Analysis):
    # GIVEN a running analysis

    # WHEN cancelling the analysis
    analysis_service.cancel_analysis(analysis_with_running_jobs.id)

    # THEN the analysis should be cancelled
    assert analysis_with_running_jobs.status == TrailblazerStatus.CANCELLED

    # THEN a comment should be added to the analysis
    assert analysis_with_running_jobs.comment


def test_update_analysis_meta_data(
    analysis_service: AnalysisService,
    analysis_with_running_jobs: Analysis,
):
    # GIVEN that the associated jobs are completed
    analysis_service.job_service.get_analysis_status.return_value = TrailblazerStatus.COMPLETED
    analysis_service.job_service.get_analysis_progression.return_value = 100

    # WHEN updating the analysis
    analysis_service.update_analysis_meta_data(analysis_with_running_jobs.id)

    # THEN the analysis should be completed
    assert analysis_with_running_jobs.status == TrailblazerStatus.COMPLETED
    assert analysis_with_running_jobs.progress == 100
