from trailblazer.clients.tower.models import TowerTask
from trailblazer.services.tower.dtos import TowerJobInfo


def create_job_dto(task: TowerTask) -> TowerJobInfo:
    return TowerJobInfo(
        job_id=task.nativeId,
        name=task.process,
        status=task.status,
        started_at=task.start,
        elapsed=int(task.duration / 60),
    )
