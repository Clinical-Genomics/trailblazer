from flask import Request


def parse_query_params(request: Request) -> dict:
    query_params = {}
    for key in request.args.keys():
        if key.endswith("[]"):
            query_params[key[:-2]] = request.args.getlist(key)
        else:
            query_params[key] = request.args.get(key)
    return query_params
