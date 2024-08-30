from trailblazer.clients.tower.models import TowerTask
from trailblazer.store.models import Job


def create_job_from_tower_task(task: TowerTask) -> Job:
    return Job(
        slurm_id=task.nativeId,
        name=task.process,
        status=task.status,
        started_at=task.start,
        elapsed=int(task.duration / 60),
    )
