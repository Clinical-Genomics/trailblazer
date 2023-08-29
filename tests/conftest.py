from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Generator, List

import pytest

from tests.apps.tower.conftest import CaseName, TowerTaskResponseFile
from tests.mocks.store_mock import MockStore
from tests.store.utils.store_helper import StoreHelpers
from trailblazer.apps.tower.models import TowerTask
from trailblazer.constants import TOWER_TIMESTAMP_FORMAT, FileFormat, TrailblazerStatus
from trailblazer.io.controller import ReadFile


@pytest.fixture(scope="session", name="username")
def fixture_username() -> str:
    """Return a username."""
    return "Paul Anderson"


@pytest.fixture(scope="session", name="archived_username")
def fixture_archived_username() -> str:
    """Return an archived username."""
    return "Archived User"


@pytest.fixture(scope="session", name="archived_user_email")
def fixture_archived_user_email() -> str:
    """Return an archived user email."""
    return "archived.user@magnolia.com"


@pytest.fixture(scope="session", name="user_email")
def fixture_user_email() -> str:
    """Return an user email."""
    return "paul.anderson@magnolia.com"


@pytest.fixture(scope="session", name="fixtures_dir")
def fixture_fixtures_dir() -> Path:
    """Return the path to the fixtures' dir."""
    return Path("tests", "fixtures")


@pytest.fixture(scope="session", name="analysis_data_path")
def fixture_analysis_data_path(fixtures_dir: Path) -> Path:
    """Return the path to an analysis data file."""
    return Path(fixtures_dir, "analysis-data.yaml")


@pytest.fixture(name="analysis_data", scope="function")
def fixture_analysis_data(analysis_data_path: Path) -> Dict[str, list]:
    """Return content of the analysis data file."""
    return ReadFile.get_content_from_file(file_format=FileFormat.YAML, file_path=analysis_data_path)


@pytest.fixture(scope="session", name="squeue_stream_jobs")
def fixture_squeue_stream_jobs() -> str:
    """Return a squeue output stream."""
    return """JOBID,NAME,STATE,TIME_LIMIT,TIME,START_TIME
690994,gatk_genotypegvcfs2,COMPLETED,10:00:00,1:01:52,2020-10-22T11:43:33
702463,bwa_mem_ACC3218A1,COMPLETED,1-06:00:00,1-1:28:12,2020-10-27T23:06:34
690992,gatk_genotypegvcfs3,COMPLETED,10:00:00,5:54,2020-10-22T11:43:02
690988,gatk_genotypegvcfs4,RUNNING,10:00:00,0:19,N/A
690989,gatk_genotypegvcfs5,PENDING,10:00:00,0:00,N/A"""


@pytest.fixture(name="trailblazer_tmp_dir")
def fixture_trailblazer_tmp_dir(tmpdir_factory) -> Path:
    """Return a temporary directory for Trailblazer testing."""
    return tmpdir_factory.mktemp("trailblazer_tmp")


@pytest.fixture(name="trailblazer_context")
def fixture_trailblazer_context(analysis_store: MockStore) -> Dict[str, MockStore]:
    """Trailblazer context to be used in CLI."""
    return {"trailblazer": analysis_store}


@pytest.fixture(name="store")
def fixture_store() -> Generator[MockStore, None, None]:
    """Empty Trailblazer database."""
    _store = MockStore(uri="sqlite://")
    _store.setup()
    yield _store
    _store.drop_all()


@pytest.fixture(scope="function", name="info_store")
def fixture_info_store(store: MockStore) -> Generator[MockStore, None, None]:
    """A Trailblazer database wih a populated info table."""
    StoreHelpers.add_info(store=store)
    yield store


@pytest.fixture(scope="function", name="job_store")
def fixture_job_store(
    store: MockStore,
) -> Generator[MockStore, None, None]:
    """A Trailblazer database wih a populated job table."""
    statuses: List[str] = [TrailblazerStatus.COMPLETED, TrailblazerStatus.FAILED]
    for index, status in enumerate(statuses):
        StoreHelpers.add_job(
            analysis_id=index, name=str(index), slurm_id=index, status=status, store=store
        )
    yield store


@pytest.fixture(scope="function", name="user_store")
def fixture_user_store(
    archived_user_email: str,
    archived_username: str,
    user_email: str,
    username: str,
    store: MockStore,
) -> Generator[MockStore, None, None]:
    """A Trailblazer database wih a populated user table."""
    StoreHelpers.add_user(email=user_email, name=username, store=store)
    StoreHelpers.add_user(
        email=archived_user_email, name=archived_username, is_archived=True, store=store
    )
    yield store


@pytest.fixture(name="raw_analyses", scope="function")
def fixture_raw_analyses(analysis_data: Dict[str, List[Dict]]) -> List[dict]:
    """Return raw analyses data."""
    analyses: List[dict] = []
    for analysis in analysis_data["analyses"]:
        analysis["case_name"] = analysis["family"]
        analyses.append(analysis)
    return analyses


@pytest.fixture(name="analysis_store")
def fixture_analysis_store(
    analysis_data: Dict[str, list],
    archived_user_email: str,
    archived_username: str,
    raw_analyses: List[dict],
    store: MockStore,
) -> Generator[MockStore, None, None]:
    """A sample Trailblazer database populated with pending analyses."""
    StoreHelpers.add_user(
        email=archived_user_email, name=archived_username, is_archived=True, store=store
    )
    for user_data in analysis_data["users"]:
        store.add_user(name=user_data["name"], email=user_data["email"])
    for raw_analysis in raw_analyses:
        raw_analysis["user"] = store.get_user(email=raw_analysis["user"])
        store.add(store.Analysis(**raw_analysis))
    store.commit()
    yield store


@pytest.fixture(name="timestamp_now", scope="session")
def fixture_timestamp_now() -> datetime:
    """Return a time stamp of today's date in date time format."""
    return datetime.now()


@pytest.fixture(name="timestamp_yesterday", scope="session")
def fixture_timestamp_yesterday(timestamp_now: datetime) -> datetime:
    """Return a time stamp of yesterday's date in date time format."""
    return timestamp_now - timedelta(days=1)


@pytest.fixture(name="tower_jobs")
def fixture_tower_jobs(analysis_id, started_at, slurm_id, tower_task_name) -> List[dict]:
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


@pytest.fixture(name="analysis_id")
def fixture_analysis_id() -> int:
    """Return a mock ID of the analysis in the Trailblazer database."""
    return 1


@pytest.fixture(name="started_at", scope="session")
def fixture_started_at() -> datetime:
    """Returns a started at date."""
    return datetime.strptime("2023-04-04T08:11:27Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture(name="slurm_id", scope="session")
def fixture_slurm_id() -> str:
    """Returns a slurm id."""
    return "4611827"


@pytest.fixture(name="tower_task_name", scope="session")
def fixture_tower_task_name() -> str:
    """Returns a NF Tower task name."""
    return "NFCORE_RNAFUSION:RNAFUSION:INPUT_CHECK:SAMPLESHEET_CHECK"


@pytest.fixture(scope="session")
def case_name() -> str:
    """Return a case name."""
    return CaseName.RUNNING


@pytest.fixture(scope="session")
def case_name_not_in_db() -> str:
    """Return a case name not present in database."""
    return "case_name_not_in_db"


@pytest.fixture(scope="session")
def failed_analysis_case_name() -> str:
    """Return a case name for a failed analysis."""
    return "crackpanda"


@pytest.fixture(scope="session")
def ongoing_analysis_case_name() -> str:
    """Return a case name for an ongoing analysis."""
    return "blazinginsect"


@pytest.fixture(name="tower_task", scope="session")
def fixture_tower_task() -> TowerTask:
    """Return a Tower task."""
    tower_task_running_content: dict = ReadFile.get_content_from_file(
        file_format=FileFormat.JSON, file_path=TowerTaskResponseFile.RUNNING
    )
    return TowerTask(**tower_task_running_content["tasks"][0]["task"])
