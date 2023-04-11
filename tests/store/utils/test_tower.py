from trailblazer.constants import TrailblazerStatus
from trailblazer.store.utils.tower import TowerTask


def test_tower_task_properties(
    tower_task: TowerTask,
    created_at,
    started_at,
    last_updated,
    duration,
    slurm_id,
    task_name,
) -> None:
    """Assess that TowerTask returns the right properties."""

    # GIVEN a tower task

    # THEN properties should be as expected
    assert tower_task.name == task_name
    assert tower_task.slurm_id == slurm_id
    assert tower_task.status == TrailblazerStatus.COMPLETED.value
    assert tower_task.date_created == created_at
    assert tower_task.last_updated == last_updated
    assert tower_task.start == started_at
    assert tower_task.duration == duration
    assert tower_task.is_complete is True
