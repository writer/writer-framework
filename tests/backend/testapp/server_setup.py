import typing

import streamsync.serve

if typing.TYPE_CHECKING:
    from fastapi import FastAPI

# Returns the FastAPI application associated with the streamsync server.
asgi_app: 'FastAPI' = streamsync.serve.app

@asgi_app.get("/probes/healthcheck")
def hello():
    return "1"
