import datetime as dt

from trailblazer.constants import TOWER_TIMESPAM_FORMAT, TrailblazerStatus
from trailblazer.store.utils.tower import TowerTask


def test_tower_task_properties(tower_task: TowerTask) -> None:
    """Assess that TowerTask returns the right properties."""

    # GIVEN a tower task

    # THEN properties should be as expected
    assert tower_task.name == "NFCORE_RNAFUSION:RNAFUSION:INPUT_CHECK:SAMPLESHEET_CHECK"
    assert tower_task.slurm_id == "4611827"
    assert tower_task.status == TrailblazerStatus.COMPLETED.value
    assert tower_task.date_created == dt.datetime.strptime(
        "2023-04-04T08:11:24Z", TOWER_TIMESPAM_FORMAT
    )
    assert tower_task.last_updated == dt.datetime.strptime(
        "2023-04-04T08:11:28Z", TOWER_TIMESPAM_FORMAT
    )
    assert tower_task.start == dt.datetime.strptime("2023-04-04T08:11:27Z", TOWER_TIMESPAM_FORMAT)
    assert tower_task.duration == 3798
    assert tower_task.is_complete == True
