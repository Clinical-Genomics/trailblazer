from trailblazer.containers import Container
import trailblazer.server.api

container = Container()


def setup_dependency_injection():
    container.wire(modules=[trailblazer.server.api])
