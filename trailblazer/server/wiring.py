from trailblazer.containers import Container

container = Container()


def setup_dependency_injection() -> Container:
    import trailblazer.cli.core
    import trailblazer.server.api

    container.wire(modules=[trailblazer.server.api, trailblazer.cli.core])
    return container
