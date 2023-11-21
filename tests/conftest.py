from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Generator

import pytest
from sqlalchemy.orm import Session

from tests.apps.tower.conftest import (
    TOWER_ID,
    CaseId,
    TowerResponseFile,
    TowerTaskResponseFile,
)
from tests.mocks.store_mock import MockStore
from tests.store.utils.store_helper import StoreHelpers
from trailblazer.apps.tower.models import TowerTask
from trailblazer.constants import (
    TOWER_TIMESTAMP_FORMAT,
    FileExtension,
    FileFormat,
    TrailblazerStatus,
)
from trailblazer.io.controller import ReadFile
from trailblazer.store.database import (
    create_all_tables,
    drop_all_tables,
    get_session,
    initialize_database,
)
from trailblazer.store.models import Analysis
from trailblazer.store.store import Store


@pytest.fixture(scope="session")
def analysis_id_does_not_exist() -> int:
    return 123456789666


@pytest.fixture(scope="session")
def analysis_comment() -> str:
    """Return a comment."""
    return "a comment"


@pytest.fixture(scope="session")
def tower_id() -> str:
    """Return a NF Tower id."""
    return TOWER_ID


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
def squeue_dir(fixtures_dir: Path) -> Path:
    """Return the path to the squeue fixture directory."""
    return Path(fixtures_dir, "squeue")


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
def trailblazer_tmp_dir(tmpdir_factory) -> Path:
    """Return a temporary directory for Trailblazer testing."""
    return tmpdir_factory.mktemp("trailblazer_tmp")


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
    StoreHelpers.add_user(email=user_email, name=username)
    StoreHelpers.add_user(email=archived_user_email, name=archived_username, is_archived=True)
    yield store


@pytest.fixture(scope="function")
def raw_analyses(analysis_data: dict[str, list[Dict]]) -> list[dict]:
    """Return raw analyses data."""
    analyses: list[dict] = []
    for analysis in analysis_data["analyses"]:
        analysis["case_id"] = analysis["family"]
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
    StoreHelpers.add_user(email=archived_user_email, name=archived_username, is_archived=True)
    for user_data in analysis_data["users"]:
        store.add_user(name=user_data["name"], email=user_data["email"])
    for raw_analysis in raw_analyses:
        raw_analysis["user"] = store.get_user(email=raw_analysis["user"])
        raw_analysis["family"] = raw_analysis.pop("case_id")
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
            status=TrailblazerStatus.PENDING.value,
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


@pytest.fixture(scope="session")
def ongoing_analysis_case_id() -> str:
    """Return a case id for an ongoing analysis."""
    return "blazinginsect"


@pytest.fixture(scope="session")
def tower_task() -> TowerTask:
    """Return a Tower task."""
    tower_task_running_content: dict = ReadFile.get_content_from_file(
        file_format=FileFormat.JSON, file_path=TowerTaskResponseFile.RUNNING
    )
    return TowerTask(**tower_task_running_content["tasks"][0]["task"])


@pytest.fixture(scope="session")
def slurm_squeue_output(squeue_dir: Path) -> dict[str, str]:
    """Return SLURM squeue output for analysis started via SLURM."""
    file_postfix: str = f"squeue{FileExtension.CSV}"
    case_ids: list[str] = [
        "blazinginsect",
        "crackpanda",
        "cuddlyhen",
        "daringpidgeon",
        "escapedgoat",
        "fancymole",
        "happycow",
        "lateraligator",
        "liberatedunicorn",
        "nicemice",
        "rarekitten",
        "trueferret",
    ]
    return {
        case_id: Path(squeue_dir, f"{case_id}_{file_postfix}").as_posix() for case_id in case_ids
    }


@pytest.fixture(scope="session")
def tower_case_config() -> dict[str, dict]:
    """Return a Tower case configs."""
    return {
        CaseId.RUNNING: {
            "workflow_response_file": TowerResponseFile.RUNNING,
            "tasks_response_file": TowerTaskResponseFile.RUNNING,
            "tower_id": TOWER_ID,
            "analysis_id": 1,
        },
        CaseId.PENDING: {
            "workflow_response_file": TowerResponseFile.PENDING,
            "tasks_response_file": TowerTaskResponseFile.PENDING,
            "tower_id": TOWER_ID,
            "analysis_id": 1,
        },
        CaseId.COMPLETED: {
            "workflow_response_file": TowerResponseFile.COMPLETED,
            "tasks_response_file": TowerTaskResponseFile.COMPLETED,
            "tower_id": TOWER_ID,
            "analysis_id": 1,
        },
    }
