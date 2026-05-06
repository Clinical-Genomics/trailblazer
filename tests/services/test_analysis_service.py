from unittest.mock import Mock, create_autospec

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

import trailblazer.services.analysis_service.analysis_service as service
from tests.typed_mock import TypedMock, create_typed_mock
from trailblazer.constants import TrailblazerStatus
from trailblazer.dto import AnalysisUpdateRequest
from trailblazer.dto.update_analyses import AnalysisUpdate, UpdateAnalyses
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.job_service.job_service import JobService
from trailblazer.store.models import Analysis, User
from trailblazer.store.store import Store


def test_patch_analyses_delivered(
    mocker: MockerFixture,
):
    # GIVEN a store with two analyses and a user
    store: Store = create_autospec(Store)
    analysis_1: Analysis = create_autospec(Analysis, id=1)
    analysis_2: Analysis = create_autospec(Analysis, id=2)
    store.update_analyses = Mock(return_value=[analysis_1, analysis_2])
    user = User(id=1)

    # GIVEN a store session
    session = create_autospec(Session)
    mocker.patch.object(service, "get_session", return_value=session)
    create_response_call: Mock = mocker.patch.object(service, "create_update_analyses_response")

    # GIVEN a request to mark an analysis as delivered
    analysis_update_1 = AnalysisUpdate(id=1, is_delivered=True)
    analysis_update_2 = AnalysisUpdate(id=2, is_delivered=True)
    update_analyses = UpdateAnalyses(analyses=[analysis_update_1, analysis_update_2])

    # GIVEN an AnalysisService
    analysis_service = AnalysisService(store=store, job_service=create_autospec(JobService))

    # WHEN updating the analysis
    analysis_service.update_analyses(data=update_analyses, user=user)

    # THEN the store method should have been called
    store.update_analyses.assert_called_once_with(data=update_analyses, user=user)

    # THEN the changes were persisted only once
    session.commit.assert_called_once()

    # THEN create_update_analyses_response was called with the analyses
    create_response_call.assert_called_once_with([analysis_1, analysis_2])


def test_update_analyses_store_raises_error(mocker: MockerFixture):
    # GIVEN a store that fails when calling update_analyses
    store: Store = create_autospec(Store)
    store.update_analyses = Mock(side_effect=Exception("Some fun error"))
    user = User(id=1)

    # GIVEN a store session
    session: TypedMock[Session] = create_typed_mock(Session)
    mocker.patch.object(service, "get_session", return_value=session.as_type)

    # GIVEN a request to mark an analysis as delivered
    analysis_update = AnalysisUpdate(id=1, is_delivered=True)
    update_analyses = UpdateAnalyses(analyses=[analysis_update])

    # GIVEN an AnalysisService
    analysis_service = AnalysisService(store=store, job_service=create_autospec(JobService))

    # WHEN updating the analysis
    with pytest.raises(Exception):
        analysis_service.update_analyses(data=update_analyses, user=user)

    # THEN the changes were persisted only once
    session.as_mock.commit.assert_not_called()


def test_update_analysis_success(mocker: MockerFixture):
    # GIVEN a store with an analysis and a user
    store: Store = create_autospec(Store)
    analysis: Analysis = create_autospec(Analysis, id=1)
    store.update_analysis = Mock(return_value=analysis)
    user = User(id=1)

    # GIVEN a store session
    session = create_autospec(Session)
    mocker.patch.object(service, "get_session", return_value=session)
    create_response_call: Mock = mocker.patch.object(service, "create_analysis_response")

    # GIVEN a request to update an analysis
    update_request = AnalysisUpdateRequest(
        comment="New comment",
        is_delivered=True,
        status=TrailblazerStatus.COMPLETED,
        is_visible=True,
    )

    # GIVEN an AnalysisService
    analysis_service = AnalysisService(store=store, job_service=create_autospec(JobService))

    # WHEN updating the analysis
    analysis_service.update_analysis(analysis_id=1, update=update_request, user=user)

    # THEN the store method should have been called
    store.update_analysis.assert_called_once_with(
        analysis_id=1,
        comment="New comment",
        is_delivered=True,
        status=TrailblazerStatus.COMPLETED,
        is_visible=True,
        user=user,
    )

    # THEN the changes were persisted
    session.commit.assert_called_once()

    # THEN create_analysis_response was called with the analysis
    create_response_call.assert_called_once_with(analysis)


def test_update_analysis_store_raises_error(mocker: MockerFixture):
    # GIVEN a store that fails when calling update_analysis
    store: Store = create_autospec(Store)
    store.update_analysis = Mock(side_effect=Exception("Some fun error"))
    user = User(id=1)

    # GIVEN a store session
    session = create_autospec(Session)
    mocker.patch.object(service, "get_session", return_value=session)

    # GIVEN a request to update an analysis
    update_request = AnalysisUpdateRequest(
        comment="New comment",
        is_delivered=True,
        status=TrailblazerStatus.COMPLETED,
        is_visible=True,
    )

    # GIVEN an AnalysisService
    analysis_service = AnalysisService(store=store, job_service=create_autospec(JobService))

    # WHEN updating the analysis
    with pytest.raises(Exception):
        analysis_service.update_analysis(analysis_id=1, update=update_request, user=user)

    # THEN the changes were not persisted
    session.commit.assert_not_called()


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
