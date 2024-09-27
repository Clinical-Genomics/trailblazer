from trailblazer.containers import Container
from trailblazer.models import Config


def setup_dependency_injection(validated_config: Config = None) -> Container:
    import trailblazer.cli.core
    import trailblazer.server.api

    container = Container()
    if validated_config:
        container.tower_access_token = validated_config.tower_base_url
        container.tower_base_url = validated_config.tower_base_url
        container.tower_workspace_id = validated_config.tower_workspace_id
    container.wire(modules=[trailblazer.server.api, trailblazer.cli.core])
    return container
