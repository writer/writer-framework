import os

import uvicorn
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Response

import streamsync.serve


def app_path(app_name: str) -> str:
    return os.path.join(os.path.dirname(__file__), app_name)

root_asgi_app = FastAPI(lifespan=streamsync.serve.lifespan)
sub_asgi_app_1 = streamsync.serve.get_asgi_app(app_path("hello"), "edit", enable_remote_edit=True)
sub_asgi_app_2 = streamsync.serve.get_asgi_app(app_path("default"), "edit", enable_remote_edit=True)
sub_asgi_app_3 = streamsync.serve.get_asgi_app(app_path("quickstart"), "edit", enable_remote_edit=True)

root_asgi_app.mount("/hello/", sub_asgi_app_1)
root_asgi_app.mount("/default/", sub_asgi_app_2)
root_asgi_app.mount("/quickstart/", sub_asgi_app_3)



@root_asgi_app.get("/")
async def init():
    links = [
        f'<li><a href="/hello">hello</a></li>',
        f'<li><a href="/default"">default</a></li>',
        f'<li><a href="/quickstart">quickstart</a></li>',
    ]

    return HTMLResponse("""
        <h1>Streamsync review app</h1>
        <ul>
        """ + "\n".join(links) + """
        </ul>
        """, status_code=200)

uvicorn.run(root_asgi_app,
    host="0.0.0.0",
    port=os.getenv('PORT', 8000),
    log_level="warning",
    ws_max_size=streamsync.serve.MAX_WEBSOCKET_MESSAGE_SIZE)