import pytest
import ruamel.yaml

from tests.mocks.store_mock import MockStore


@pytest.fixture(scope="function")
def trailblazer_context(sample_store: MockStore) -> dict:
    """Trailblazer context to be used in CLI."""
    return {"trailblazer": sample_store}


@pytest.yield_fixture(scope="function")
def store():
    """Empty Trailblazer database."""
    _store = MockStore(uri="sqlite://")
    _store.setup()
    yield _store
    _store.drop_all()


@pytest.yield_fixture(scope="function")
def sample_store(store: MockStore):
    """A sample Trailblazer database populated with pending analyses."""
    sample_data = ruamel.yaml.safe_load(open("tests/fixtures/sample-data.yaml"))
    for user_data in sample_data["users"]:
        store.add_user(user_data["name"], user_data["email"])
    for analysis_data in sample_data["analyses"]:
        analysis_data["case_id"] = analysis_data["family"]
        analysis_data["user"] = store.user(analysis_data["user"])
        store.add(store.Analysis(**analysis_data))
    store.commit()
    yield store
