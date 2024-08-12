from trailblazer.constants import TrailblazerStatus
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.models import Analysis


def test_cancel_analysis(analysis_service: AnalysisService, running_analysis: Analysis):
    # GIVEN a running analysis

    # WHEN cancelling the analysis
    analysis_service.cancel_analysis(running_analysis.id)

    # THEN the analysis should be cancelled
    assert running_analysis.status == TrailblazerStatus.CANCELLED
    
    # THEN a comment should be added to the analysis
    assert running_analysis.comment
