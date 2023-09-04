from trailblazer.models import Config


def test_instantiate_config():
    """Tests config input against a pydantic model."""
    # GIVEN config raw input

    # WHEN instantiating a Config object
    config = Config(database="a_database", analysis_host="a_name@host.se")

    # THEN it was successfully created
    assert isinstance(config, Config)
