"""
This is a simple application to help our team to review contribution.

>>> python apps/reviewapp.py

Runs this application in public and requires authentication.

>>> export HOST=0.0.0.0; export BASICAUTH=admin:admin; python apps/reviewapp.py
"""
import base64
import os
import time

import uvicorn
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, status

import streamsync.serve

HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', '8000'))
print(f"listen on {HOST}:{PORT}")


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



@root_asgi_app.middleware("http")
async def valid_authentication(request, call_next):
    """
    Secures access to the review application using basic auth

    The username and password is stored in the BASICAUTH environment variable.
    The authentication process is sequential and when it's wrong it take one second to try again. This protection
    is sufficient to limit brute force attack.
    """
    if HOST == 'localhost':
        """
        Locally, you can launch the review application without needing to authenticate.
        
        The application bypass the authentication middleware.
        """
        return await call_next(request)

    _auth = request.headers.get('Authorization')
    if not check_permission(_auth):
        return HTMLResponse("", status.HTTP_401_UNAUTHORIZED, {"WWW-Authenticate": "Basic"})
    return await call_next(request)


def check_permission(auth) -> bool:
    """
    Secures access to the review application using basic auth

    >>> is_valid_token = check_permission('Basic dXNlcm5hbWU6cGFzc3dvcmQ=')
    """
    if auth is None:
        return False

    scheme, data = (auth or ' ').split(' ', 1)
    if scheme != 'Basic':
        return False

    username, password = base64.b64decode(data).decode().split(':', 1)
    basicauth = os.getenv('BASICAUTH')
    if auth is None:
        raise ValueError('BASICAUTH environment variable is not set')

    basicauth_part = basicauth.split(':')
    if len(basicauth_part) != 2:
        raise ValueError('BASICAUTH environment variable is not set')

    basicauth_username, basicauth_password = basicauth_part

    time.sleep(1)
    if username == basicauth_username and password == basicauth_password:
        return True
    else:
        time.sleep(1)
        return False


uvicorn.run(root_asgi_app,
    host=HOST,
    port=PORT,
    log_level="warning",
    ws_max_size=streamsync.serve.MAX_WEBSOCKET_MESSAGE_SIZE)