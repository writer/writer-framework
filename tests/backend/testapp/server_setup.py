import streamsync.serve

asgi_app = streamsync.serve.app

@asgi_app.get("/probes/healthcheck")
def hello():
    return "1"
