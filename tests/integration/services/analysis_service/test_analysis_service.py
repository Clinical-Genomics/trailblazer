from trailblazer.constants import TrailblazerStatus
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.models import Analysis


def test_updating_tower_analysis(analysis_service: AnalysisService, tower_analysis: Analysis):

    # GIVEN an analysis started with tower without any job entries but running tasks

    # WHEN updating the tower analysis
    analysis_service.update_analysis_meta_data(tower_analysis.id)

    # THEN job entries have been created for the analysis
    assert tower_analysis.jobs

    # THEN the status of the analysis is running
    assert tower_analysis.status == TrailblazerStatus.RUNNING

    # THEN the progress of the analysis is updated
    assert tower_analysis.progress > 0


def test_updating_slurm_analysis(analysis_service: AnalysisService, slurm_analysis: Analysis):

    # GIVEN an analysis started with slurm without any job entries but running jobs

    # WHEN updating the slurm analysis
    analysis_service.update_analysis_meta_data(slurm_analysis.id)

    # THEN job entries have been created for the analysis
    assert slurm_analysis.jobs

    # THEN the status of the analysis is running
    assert slurm_analysis.status == TrailblazerStatus.COMPLETED

    # THEN the progress of the analysis is updated
    assert slurm_analysis.progress > 0
