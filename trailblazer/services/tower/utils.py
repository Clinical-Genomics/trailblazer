from pathlib import Path
from trailblazer.clients.tower.models import TowerTask
from trailblazer.constants import FileFormat
from trailblazer.io.controller import ReadFile
from trailblazer.store.models import Analysis, Job


def get_tower_workflow_id(analysis: Analysis) -> str:
    file = Path(analysis.config_path)
    content: dict = ReadFile.get_content_from_file(file_format=FileFormat.YAML, file_path=file)
    return content.get(analysis.case_id)[-1]


def create_job_from_tower_task(task: TowerTask) -> Job:
    return Job(
        slurm_id=task.nativeId,
        name=task.process,
        status=task.status,
        started_at=task.start,
        elapsed=int(task.duration / 60),
    )
