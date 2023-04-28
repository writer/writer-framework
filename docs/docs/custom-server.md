# Custom server

Streamsync uses Uvicorn and serves the app in the root path i.e. `/`. If you need to use another ASGI-compatible server or fine-tune Uvicorn, you can easily do so.

## Getting the ASGI app

You can import `streamsync.serve` and use the function `get_asgi_app`. This returns an ASGI app created by FastAPI, which you can choose how to serve.

The following code can serve as a starting point. You can save this code as `serve.py` and run it with `python serve.py`.

```py
import uvicorn
import streamsync.serve

app_path = "." # . for current working directory
mode = "run" # run or edit

asgi_app = streamsync.serve.get_asgi_app(app_path, mode)

uvicorn.run(asgi_app,
    host="0.0.0.0",
    port=5328,
    log_level="warning",
    ws_max_size=streamsync.serve.MAX_WEBSOCKET_MESSAGE_SIZE)
```

Note the inclusion of the imported `ws_max_size` setting. This is important for normal functioning of the framework when dealing with bigger files.

Fine-tuning Uvicorn allows you to set up SSL, configure proxy headers, etc, which can prove vital in complex deployments.

## Multiple apps at once

Streamsync is built using relative paths, so it can be served from any path. This allows multiple apps to be simultaneously served on different paths.

The example below uses the `get_asgi_app` function to obtain two separate Streamsync apps, which are then mounted on different paths, `/app1` and `/app2`, of a FastAPI app.

```py
import uvicorn
import streamsync.serve
from fastapi import FastAPI, Response

root_asgi_app = FastAPI()
sub_asgi_app_1 = streamsync.serve.get_asgi_app("../app1", "run")
sub_asgi_app_2 = streamsync.serve.get_asgi_app("../app2", "run")

root_asgi_app.mount("/app1", sub_asgi_app_1)
root_asgi_app.mount("/app2", sub_asgi_app_2)

@root_asgi_app.get("/")
async def init():
    return Response("""
    <h1>Welcome to the App Hub</h1>
    """)

uvicorn.run(root_asgi_app,
    host="0.0.0.0",
    port=5328,
    log_level="warning",
    ws_max_size=streamsync.serve.MAX_WEBSOCKET_MESSAGE_SIZE)
```
