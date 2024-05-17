import typing

import writer.serve

if typing.TYPE_CHECKING:
    from fastapi import FastAPI

# Returns the FastAPI application associated with the Writer Framework server.
asgi_app: 'FastAPI' = writer.serve.app

@asgi_app.get("/probes/healthcheck")
def hello():
    return "1"
