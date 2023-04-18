from trailblazer.constants import TrailblazerStatus
from trailblazer.store.utils.tower import TowerTask


def test_tower_task_properties(
    tower_task: TowerTask,
    created_at,
    started_at,
    last_updated,
    tower_task_duration,
    slurm_id,
    tower_task_name,
) -> None:
    """Assess that TowerTask returns the right properties."""

    # GIVEN a tower task

    # THEN properties should be returned
    assert tower_task.process == tower_task_name
    assert tower_task.nativeId == slurm_id
    assert tower_task.status == TrailblazerStatus.COMPLETED.value
    assert tower_task.dateCreated == created_at
    assert tower_task.lastUpdated == last_updated
    assert tower_task.start == started_at
    assert tower_task.duration == tower_task_duration
    assert tower_task.is_complete is True
