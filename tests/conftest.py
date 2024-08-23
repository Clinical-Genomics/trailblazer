from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Generator

import pytest
from sqlalchemy.orm import Session

from tests.mocks.store_mock import MockStore
from tests.store.utils.store_helper import StoreHelpers
from trailblazer.clients.slurm_api_client.dto.common import SlurmAPIJobInfo
from trailblazer.clients.slurm_api_client.dto.job_response import SlurmJobResponse
from trailblazer.clients.tower.models import (
    TaskWrapper,
    TowerProgress,
    TowerTask,
    TowerTasksResponse,
    TowerWorkflow,
    TowerWorkflowResponse,
)
from trailblazer.constants import (
    PRIORITY_OPTIONS,
    TOWER_TIMESTAMP_FORMAT,
    TYPES,
    FileFormat,
    JobType,
    TrailblazerStatus,
    WorkflowManager,
)
from trailblazer.io.controller import ReadFile
from trailblazer.store.database import (
    create_all_tables,
    drop_all_tables,
    get_session,
    initialize_database,
)
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store


class CaseId:
    PENDING: str = "cuddlyhen_pending"
    RUNNING: str = "cuddlyhen"
    COMPLETED: str = "cuddlyhen_completed"


@pytest.fixture(scope="session")
def analysis_id_does_not_exist() -> int:
    return 123456789666


@pytest.fixture(scope="session")
def analysis_comment() -> str:
    """Return a comment."""
    return "a comment"


@pytest.fixture(scope="session")
def username() -> str:
    """Return a username."""
    return "Paul Anderson"


@pytest.fixture(scope="session")
def archived_username() -> str:
    """Return an archived username."""
    return "Archived User"


@pytest.fixture(scope="session")
def archived_user_email() -> str:
    """Return an archived user email."""
    return "archived.user@magnolia.com"


@pytest.fixture(scope="session")
def user_email() -> str:
    """Return an user email."""
    return "paul.anderson@magnolia.com"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return the path to the fixtures' dir."""
    return Path("tests", "fixtures")


@pytest.fixture(scope="session")
def analysis_data_path(fixtures_dir: Path) -> Path:
    """Return the path to an analysis data file."""
    return Path(fixtures_dir, "analysis-data.yaml")


@pytest.fixture(scope="function")
def analysis_data(analysis_data_path: Path) -> dict[str, list]:
    """Return content of the analysis data file."""
    return ReadFile.get_content_from_file(file_format=FileFormat.YAML, file_path=analysis_data_path)


@pytest.fixture(scope="session")
def squeue_stream_jobs() -> str:
    """Return a squeue output stream."""
    return """JOBID,NAME,STATE,TIME_LIMIT,TIME,START_TIME
690994,gatk_genotypegvcfs2,COMPLETED,10:00:00,1:01:52,2020-10-22T11:43:33
702463,bwa_mem_ACC3218A1,COMPLETED,1-06:00:00,1-1:28:12,2020-10-27T23:06:34
690992,gatk_genotypegvcfs3,COMPLETED,10:00:00,5:54,2020-10-22T11:43:02
690988,gatk_genotypegvcfs4,RUNNING,10:00:00,0:19,N/A
690989,gatk_genotypegvcfs5,PENDING,10:00:00,0:00,N/A"""


@pytest.fixture
def trailblazer_context(analysis_store: MockStore) -> dict[str, MockStore]:
    """Trailblazer context to be used in CLI."""
    return {"trailblazer_db": analysis_store}


@pytest.fixture
def store() -> Generator[MockStore, None, None]:
    """Empty Trailblazer database."""
    initialize_database("sqlite:///:memory:")
    _store = Store()
    create_all_tables()
    yield _store
    drop_all_tables()


@pytest.fixture(scope="function")
def info_store(store: MockStore) -> Generator[MockStore, None, None]:
    """A Trailblazer database wih a populated info table."""
    StoreHelpers.add_info(store=store)
    yield store


@pytest.fixture(scope="function")
def job_store(
    store: MockStore,
) -> Generator[MockStore, None, None]:
    """A Trailblazer database wih a populated job table."""
    statuses: list[str] = [TrailblazerStatus.COMPLETED, TrailblazerStatus.FAILED]
    for index, status in enumerate(statuses):
        StoreHelpers.add_job(analysis_id=index, name=str(index), slurm_id=index, status=status)
    yield store


@pytest.fixture(scope="function")
def user_store(
    archived_user_email: str,
    archived_username: str,
    user_email: str,
    username: str,
    store: MockStore,
) -> Generator[MockStore, None, None]:
    """A Trailblazer database wih a populated user table."""
    StoreHelpers.add_user(email=user_email, name=username, abbreviation="SUS")
    StoreHelpers.add_user(
        email=archived_user_email,
        name=archived_username,
        abbreviation="SUSUS",
        is_archived=True,
    )
    yield store


@pytest.fixture(scope="function")
def raw_analyses(analysis_data: dict[str, list[Dict]]) -> list[dict]:
    """Return raw analyses data."""
    analyses: list[dict] = []
    for analysis in analysis_data["analyses"]:
        analyses.append(analysis)
    return analyses


@pytest.fixture
def analysis_store(
    analysis_data: dict[str, list],
    archived_user_email: str,
    archived_username: str,
    raw_analyses: list[dict],
    store: MockStore,
) -> Generator[MockStore, None, None]:
    """A sample Trailblazer database populated with pending analyses."""
    session: Session = get_session()
    StoreHelpers.add_user(
        email=archived_user_email, name=archived_username, is_archived=True, abbreviation="abbrev"
    )
    for user_data in analysis_data["users"]:
        store.add_user(
            name=user_data["name"],
            email=user_data["email"],
            abbreviation=user_data["abbreviation"],
        )
    for raw_analysis in raw_analyses:
        raw_analysis["user"] = store.get_user(email=raw_analysis["user"])
        raw_analysis["case_id"] = raw_analysis.pop("case_id")
        session.add(Analysis(**raw_analysis))
    yield store


@pytest.fixture(scope="session")
def timestamp_now() -> datetime:
    """Return a time stamp of today's date in date time format."""
    return datetime.now()


@pytest.fixture(scope="session")
def timestamp_yesterday(timestamp_now: datetime) -> datetime:
    """Return a time stamp of yesterday's date in date time format."""
    return timestamp_now - timedelta(days=1)


@pytest.fixture(scope="session")
def timestamp_old() -> datetime:
    """Return an old time stamp in a date time format."""
    timestamp: str = "1066-10-14 00:00:00"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(timestamp, timestamp_format)


@pytest.fixture
def tower_jobs(analysis_id, started_at, slurm_id, tower_task_name) -> list[dict]:
    """Return a list of Tower Jobs."""
    return [
        dict(
            analysis_id=analysis_id,
            slurm_id=slurm_id,
            name=tower_task_name,
            started_at=started_at,
            elapsed=63,
            status=TrailblazerStatus.COMPLETED,
        ),
        dict(
            analysis_id=analysis_id,
            slurm_id="4611829",
            name="NFCORE_RNAFUSION:RNAFUSION:PIZZLY_WORKFLOW:KALLISTO_QUANT",
            started_at=None,
            elapsed=0,
            status=TrailblazerStatus.PENDING,
        ),
        dict(
            analysis_id=analysis_id,
            slurm_id="4611828",
            name="NFCORE_RNAFUSION:RNAFUSION:FASTQC",
            started_at=None,
            elapsed=0,
            status=TrailblazerStatus.PENDING,
        ),
    ]


@pytest.fixture
def analysis_id() -> int:
    """Return a mock ID of the analysis in the Trailblazer database."""
    return 1


@pytest.fixture(scope="session")
def started_at() -> datetime:
    """Returns a started at date."""
    return datetime.strptime("2023-04-04T08:11:27Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture(scope="session")
def slurm_id() -> str:
    """Returns a slurm id."""
    return "4611827"


@pytest.fixture(scope="session")
def tower_task_name() -> str:
    """Returns a NF Tower task name."""
    return "NFCORE_RNAFUSION:RNAFUSION:INPUT_CHECK:SAMPLESHEET_CHECK"


@pytest.fixture(scope="session")
def case_id() -> str:
    """Return a case id."""
    return CaseId.RUNNING


@pytest.fixture(scope="session")
def case_id_not_in_db() -> str:
    """Return a case id not present in database."""
    return "case_id_not_in_db"


@pytest.fixture(scope="session")
def failed_analysis_case_id() -> str:
    """Return a case id for a failed analysis."""
    return "crackpanda"


@pytest.fixture
def analysis_with_upload_jobs(case_id: str) -> Analysis:
    upload_job = Job(
        name="upload",
        slurm_id="123456",
        job_type=JobType.UPLOAD,
        status=TrailblazerStatus.COMPLETED,
        started_at=datetime.now(),
        elapsed=10,
    )
    analysis = Analysis(case_id=case_id)
    analysis.jobs.append(upload_job)
    session = get_session()
    session.add(analysis)
    return analysis


@pytest.fixture
def tower_analysis(analysis_store: Store, tmp_path) -> Analysis:
    case_id = "case_id"
    config_path: Path = tmp_path / "tower.yaml"
    config_path.write_text(f"case_id: {case_id}")

    analysis = Analysis(
        config_path=str(config_path),
        workflow="workflow",
        case_id="case_id",
        out_dir="out_dir",
        priority=PRIORITY_OPTIONS[0],
        started_at=datetime.now() - timedelta(weeks=1),
        status=TrailblazerStatus.PENDING,
        ticket_id="ticket_id",
        type=TYPES[0],
        workflow_manager=WorkflowManager.TOWER,
        is_visible=True,
        order_id=1,
    )
    session: Session = get_session()
    session.add(analysis)
    session.commit()
    return analysis


@pytest.fixture
def tower_tasks_response():
    task_1 = TowerTask(
        process="example_process",
        name="example_task",
        status="COMPLETED",
        nativeId="1234",
        dateCreated=datetime.now(),
        lastUpdated=datetime.now(),
        start=datetime.now(),
        module=["example_module"],
    )

    task_2 = TowerTask(
        process="example_process",
        name="example_task",
        status="RUNNING",
        nativeId="1234",
        dateCreated=datetime.now(),
        lastUpdated=datetime.now(),
        start=datetime.now(),
        module=["example_module"],
    )

    task_wrapper_1 = TaskWrapper(task=task_1)
    task_wrapper_2 = TaskWrapper(task=task_2)
    return TowerTasksResponse(tasks=[task_wrapper_1, task_wrapper_2], total=2)


@pytest.fixture
def tower_workflow_response() -> TowerWorkflowResponse:
    worfklow = TowerWorkflow(status="RUNNING")
    progress = TowerProgress(workflowProgress={}, processesProgress=[])
    return TowerWorkflowResponse(
        workflow=worfklow,
        progress=progress,
    )


@pytest.fixture
def slurm_analysis(tmp_path) -> Analysis:
    config_path: Path = tmp_path / "slurm.yaml"
    content = """---
    case_id:
    - '6123780'
    """
    config_path.write_text(content)

    analysis = Analysis(
        config_path=str(config_path),
        workflow="workflow",
        case_id="case_id",
        out_dir="out_dir",
        priority=PRIORITY_OPTIONS[0],
        started_at=datetime.now() - timedelta(weeks=1),
        status=TrailblazerStatus.PENDING,
        ticket_id="ticket_id",
        type=TYPES[0],
        workflow_manager=WorkflowManager.SLURM,
        is_visible=True,
        order_id=1,
    )
    session: Session = get_session()
    session.add(analysis)
    session.commit()
    return analysis


@pytest.fixture
def slurm_job_response() -> SlurmJobResponse:
    job_info = SlurmAPIJobInfo(
        job_id=12345,
        job_state=["COMPLETED"],
        name="Test Job",
    )
    return SlurmJobResponse(jobs=[job_info], errors=None, warnings=None)
