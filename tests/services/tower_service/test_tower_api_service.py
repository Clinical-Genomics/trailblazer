from trailblazer.clients.tower.models import TowerTasksResponse
from trailblazer.services.tower.tower_api_service import TowerAPIService
from trailblazer.store.models import Analysis


def test_update_jobs(
    tower_service: TowerAPIService,
    tower_analysis: Analysis,
    tower_tasks_response: TowerTasksResponse,
):
    # GIVEN an analysis started in tower without any jobs

    # GIVEN that some tasks for it have started running
    tower_service.client.get_tasks.return_value = tower_tasks_response

    # WHEN updating the jobs
    tower_service.update_jobs(tower_analysis.id)

    # THEN the jobs should be updated
    assert tower_analysis.jobs
