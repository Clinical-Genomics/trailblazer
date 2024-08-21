from trailblazer.constants import TrailblazerStatus
from trailblazer.dto.update_analyses import AnalysisUpdate, UpdateAnalyses
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.models import Analysis, User
from trailblazer.store.store import Store


def test_patch_analyses_delivered(
    analysis_store: Store,
    analysis_id: int,
    analysis_service: AnalysisService,
):
    # GIVEN a request to mark an analysis as delivered
    analysis: Analysis = analysis_store.get_analysis_with_id(analysis_id)
    analysis_update = AnalysisUpdate(id=analysis_id, is_delivered=True)
    update_analyses = UpdateAnalyses(analyses=[analysis_update])
    user = User(id=1)

    # WHEN updating the analysis
    analysis_service.update_analyses(data=update_analyses, user=user)

    # THEN the analysis should be marked as delivered
    assert analysis.delivered_by


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
