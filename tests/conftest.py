import datetime as dt
from pathlib import Path
from typing import Dict, List, Generator

import pytest

from tests.apps.tower.conftest import CaseIDs, TowerTaskResponseFile
from tests.mocks.store_mock import MockStore
from trailblazer.apps.tower.models import TowerTask
from trailblazer.constants import TOWER_TIMESTAMP_FORMAT, TrailblazerStatus, FileFormat
from trailblazer.io.controller import ReadFile
from tests.store.utils.store_helper import StoreHelpers


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


@pytest.fixture(scope="session", name="sample_data_path")
def fixture_sample_data_path(fixtures_dir: Path) -> Path:
    """Return the path to the sample data file."""
    return Path(fixtures_dir, "sample-data.yaml")


@pytest.fixture(name="sample_data")
def fixture_sample_data(sample_data_path: Path) -> Dict[str, list]:
    """Return content of the sample data file."""
    return ReadFile.get_content_from_file(file_format=FileFormat.YAML, file_path=sample_data_path)


@pytest.fixture(name="trailblazer_tmp_dir")
def fixture_trailblazer_tmp_dir(tmpdir_factory) -> Path:
    """Return a temporary directory for Trailblazer testing."""
    return tmpdir_factory.mktemp("trailblazer_tmp")


@pytest.fixture(name="trailblazer_context")
def fixture_trailblazer_context(sample_store: MockStore) -> Dict[str, MockStore]:
    """Trailblazer context to be used in CLI."""
    return {"trailblazer": sample_store}


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


@pytest.fixture(name="sample_store")
def fixture_sample_store(
    archived_user_email: str, archived_username: str, sample_data: Dict[str, list], store: MockStore
) -> Generator[MockStore, None, None]:
    """A sample Trailblazer database populated with pending analyses."""
    StoreHelpers.add_user(
        email=archived_user_email, name=archived_username, is_archived=True, store=store
    )
    for user_data in sample_data["users"]:
        store.add_user(user_data["name"], user_data["email"])
    for analysis_data in sample_data["analyses"]:
        analysis_data["case_id"] = analysis_data["family"]
        analysis_data["user"] = store.user(analysis_data["user"])
        store.add(store.Analysis(**analysis_data))
    store.commit()
    yield store


@pytest.fixture(name="timestamp_now", scope="session")
def fixture_timestamp_now() -> dt.datetime:
    """Return a time stamp of today's date in date time format."""
    return dt.datetime.now()


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
            status=TrailblazerStatus.COMPLETED.value,
        ),
        dict(
            analysis_id=analysis_id,
            slurm_id="4611829",
            name="NFCORE_RNAFUSION:RNAFUSION:PIZZLY_WORKFLOW:KALLISTO_QUANT",
            started_at=None,
            elapsed=0,
            status=TrailblazerStatus.PENDING.value,
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
def fixture_started_at() -> dt.datetime:
    """Returns a started at date."""
    return dt.datetime.strptime("2023-04-04T08:11:27Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture(name="slurm_id", scope="session")
def fixture_slurm_id() -> str:
    """Returns a slurm id."""
    return "4611827"


@pytest.fixture(name="tower_task_name", scope="session")
def fixture_tower_task_name() -> str:
    """Returns a NF Tower task name."""
    return "NFCORE_RNAFUSION:RNAFUSION:INPUT_CHECK:SAMPLESHEET_CHECK"


@pytest.fixture(name="case_id", scope="session")
def fixture_case_id() -> str:
    """Return a case ID."""
    return CaseIDs.RUNNING


@pytest.fixture(name="tower_task", scope="session")
def fixture_tower_task() -> TowerTask:
    """Return a Tower task."""
    tower_task_running_content: dict = ReadFile.get_content_from_file(
        file_format=FileFormat.JSON, file_path=TowerTaskResponseFile.RUNNING
    )
    return TowerTask(**tower_task_running_content["tasks"][0]["task"])
