from http import HTTPStatus

from trailblazer.server.api import blueprint


@blueprint.route("/endpoint", methods=["GET"])
def authorized_endpoint():
    return HTTPStatus.OK

def test_before_request_success():
    pass
