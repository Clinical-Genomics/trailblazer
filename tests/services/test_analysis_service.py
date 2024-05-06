from trailblazer.constants import TrailblazerStatus
from trailblazer.dto.update_analyses import AnalysisUpdate, UpdateAnalyses
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.models import Analysis, User
from trailblazer.store.store import Store


def test_patch_analyses_delivered(
    analysis_store: Store, analysis_id: int, analysis_service: AnalysisService
):
    analysis: Analysis = analysis_store.get_analysis_with_id(analysis_id)
    analysis_update = AnalysisUpdate(id=analysis_id, is_delivered=True)
    update_analyses = UpdateAnalyses(analyses=[analysis_update])
    user = User(id=1)

    analysis_service.update_analyses(data=update_analyses, user=user)

    assert analysis.delivered_by


def test_update_analysis_status(analysis_store: Store, analysis_service: AnalysisService):
    # GIVEN a store with ongoing analyses
    ongoing_analyses: list[Analysis] = analysis_store.get_ongoing_analyses()
    assert ongoing_analyses

    # GIVEN that some analyses are completed

    # WHEN updating the status of the analyses
    analysis_service.update_ongoing_analyses()

    # THEN the status of some analyses should be updated
    currently_ongoing_analyses: list[Analysis] = analysis_store.get_ongoing_analyses()
    assert len(currently_ongoing_analyses) < len(ongoing_analyses)
