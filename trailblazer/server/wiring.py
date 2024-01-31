from trailblazer.containers import Container
import trailblazer.server.api
import trailblazer.cli.core

container = Container()


def setup_dependency_injection() -> Container:
    container.wire(modules=[trailblazer.server.api, trailblazer.cli.core])
    return container
