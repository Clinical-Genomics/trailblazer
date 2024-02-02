from trailblazer.containers import Container

container = Container()


def setup_dependency_injection() -> Container:
    import trailblazer.server.api
    import trailblazer.cli.core

    container.wire(modules=[trailblazer.server.api, trailblazer.cli.core])
    return container
