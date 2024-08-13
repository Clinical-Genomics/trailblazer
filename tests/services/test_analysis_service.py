from trailblazer.constants import TrailblazerStatus
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.job_service.job_service import JobService
from trailblazer.store.models import Analysis


def test_cancel_analysis(analysis_service: AnalysisService, running_analysis: Analysis):
    # GIVEN a running analysis

    # WHEN cancelling the analysis
    analysis_service.cancel_analysis(running_analysis.id)

    # THEN the analysis should be cancelled
    assert running_analysis.status == TrailblazerStatus.CANCELLED

    # THEN a comment should be added to the analysis
    assert running_analysis.comment


def test_update_analysis_meta_data(
    analysis_service: AnalysisService,
    running_analysis: Analysis,
):
    # GIVEN that the associated jobs are completed
    analysis_service.job_service.get_analysis_status.return_value = TrailblazerStatus.COMPLETED
    analysis_service.job_service.get_analysis_progression.return_value = 100

    # WHEN updating the analysis
    analysis_service.update_analysis_meta_data(running_analysis.id)

    # THEN the analysis should be completed
    assert running_analysis.status == TrailblazerStatus.COMPLETED
    assert running_analysis.progress == 100
