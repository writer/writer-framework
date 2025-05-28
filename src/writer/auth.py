import asyncio
import dataclasses
import logging
import os.path
import time
from abc import ABCMeta, abstractmethod
from typing import Callable, Dict, Optional
from urllib.parse import urlparse

from authlib.integrations.requests_client.oauth2_session import OAuth2Session  # type: ignore
from fastapi import Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import writer.serve
from writer.core import session_manager
from writer.serve import WriterFastAPI
from writer.ss_types import InitSessionRequestPayload

logger = logging.getLogger('writer')

# Dictionary for storing failed attempts {ip_address: timestamp}
failed_attempts: Dict[str, float] = {}

class Unauthorized(Exception):
    """
    This exception allows you to reject the authentication of a user.

    >>>
    """
    def __init__(self, status_code = 401, message = "Unauthorized", more_info = ""):
        self.status_code = status_code
        self.message = message
        self.more_info = more_info


class Auth:
    """
    Interface to implement authentication in Writer Framework.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def register(self,
                 asgi_app: WriterFastAPI,
                 callback: Optional[Callable[[Request, str, dict], None]] = None,
                 unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None
    ):
        raise NotImplementedError

@dataclasses.dataclass
class BasicAuth(Auth):
    """
    Configure Writer Framework to use Basic Authentication. If this is set, Writer Framework will
    ask anonymous users to authenticate using Basic Authentication.

    >>> _auth = auth.BasicAuth(
    >>>     login=os.getenv('LOGIN'),
    >>>     password=os.getenv('PASSWORD')
    >>> )
    >>> writer.server.register_auth(_auth)

    Brute force protection
    ----------------------

    A simple brute force protection is implemented by default. If a user fails to log in, the IP of this user is blocked.
    Writer framework will ban the IP from either the `X-Forwarded-For` header or the `X-Real-IP` header or the client IP address.

    When a user fails to log in, they wait 1 second before they can try again. This time can be modified by
    modifying the value of `delay_after_failure`.

    >>> _auth = auth.BasicAuth(
    >>>     login=os.getenv('LOGIN'),
    >>>     password=os.getenv('PASSWORD')
    >>>     delay_after_failure=5 # 5 seconds delay after a failed login
    >>> )
    >>> writer.server.register_auth(_auth)

    The user is stuck by default after a failure.

    >>> _auth = auth.BasicAuth(
    >>>     login=os.getenv('LOGIN'),
    >>>     password=os.getenv('PASSWORD'),
    >>>     delay_after_failure=5,
    >>>     block_user_after_failure=False
    >>> )
    """
    login: str
    password: str
    delay_after_failure: int = 1  # limit attempt when authentication fail (reduce brute force risk)
    block_user_after_failure: bool = True  # delay the answer to the user after a failed login

    callback_func: Optional[Callable[[Request, str, dict], None]] = None  # Callback to validate user authentication
    unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None  # Callback to build its own page when a user is not allowed


    def register(self,
                 asgi_app: WriterFastAPI,
                 callback: Optional[Callable[[Request, str, dict], None]] = None,
                 unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None):

        self.unauthorized_action = unauthorized_action
        self.callback_func = callback

        @asgi_app.middleware("http")
        async def basicauth_middleware(request: Request, call_next):
            import base64
            client_ip = _client_ip(request)

            try:
                if client_ip in failed_attempts and time.time() - failed_attempts[client_ip] < self.delay_after_failure:
                    remaining_time = int(self.delay_after_failure - (time.time() - failed_attempts[client_ip]))
                    raise Unauthorized(status_code=429, message="Too Many Requests", more_info=f"You can try to log in every {self.delay_after_failure}s. Your next try is in {remaining_time}s.")

                session_id = session_manager.generate_session_id()
                _auth = request.headers.get('Authorization')
                if _auth is None:
                    return HTMLResponse("", status.HTTP_401_UNAUTHORIZED, {"WWW-Authenticate": "Basic"})

                scheme, data = (_auth or ' ').split(' ', 1)
                if scheme != 'Basic':
                    return HTMLResponse("", status.HTTP_401_UNAUTHORIZED, {"WWW-Authenticate": "Basic"})

                username, password = base64.b64decode(data).decode().split(':', 1)
                if self.callback_func:
                    self.callback_func(request, session_id, {'username': username})
                else:
                    if username != self.login or password != self.password:
                        raise Unauthorized()

                return await call_next(request)
            except Unauthorized as exc:
                if exc.status_code != 429:
                    failed_attempts[client_ip] = time.time()

                    if self.block_user_after_failure:
                        await asyncio.sleep(self.delay_after_failure)

                if self.unauthorized_action is not None:
                    return self.unauthorized_action(request, exc)
                else:
                    templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
                    return templates.TemplateResponse(request=request, name="auth_unauthorized.html", status_code=exc.status_code, context={
                        "status_code": exc.status_code,
                        "message": exc.message,
                        "more_info": exc.more_info
                    })

@dataclasses.dataclass
class Oidc(Auth):
    """
    Configure Writer Framework to use OpenID Connect. If this is set, Writer Framework will
    redirect anonymous users to OpenID Connect issuer.

    The issuer will then
    authenticate the user and redirect back to the Writer Framework application with
    an authorization code. The Writer Framework application will then exchange the
    authorization code for an access token and use the access token to
    authenticate the user and fetch user information.

    >>> oidc = Oidc(
    ...     client_id="xxxxxxx",
    ...     client_secret="xxxxxxxxxxxxx.apps.googleusercontent.com",
    ...     url_authorize="https://accounts.google.com/o/oauth2/auth",
    ...     url_oauthtoken="https://oauth2.googleapis.com/token",
    ...     url_userinfo="https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
    ... )
    >>> writer.server.register_auth(oidc)

    """
    client_id: str
    client_secret: str
    host_url: str
    url_authorize: str
    url_oauthtoken: str
    scope: str = "openid email profile"
    callback_authorize: str = "authorize"
    url_userinfo: Optional[str] = None
    app_static_public: bool = False

    authlib: OAuth2Session = None
    callback_func: Optional[Callable[[Request, str, dict], None]] = None # Callback to validate user authentication
    unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None # Callback to build its own page when a user is not allowed


    def register(self,
                 asgi_app: WriterFastAPI,
                 callback: Optional[Callable[[Request, str, dict], None]] = None,
                 unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None
                 ):

        redirect_url = urljoin(self.host_url, self.callback_authorize)
        host_url_path = urlpath(self.host_url)
        callback_authorize_path = urljoin(host_url_path, self.callback_authorize)

        auth_authorized_prefix_paths = []
        auth_authorized_routes = [callback_authorize_path]

        for asset_path in writer.serve.wf_root_static_assets():
            if asset_path.is_file():
                auth_authorized_routes.append(urljoin(host_url_path, asset_path.name))
            elif asset_path.is_dir():
                auth_authorized_prefix_paths.append(urljoin(host_url_path, asset_path.name))

        if self.app_static_public is True:
            auth_authorized_prefix_paths += [urljoin(host_url_path, "static"), urljoin(host_url_path, "extensions")]

        logger.debug(f"[auth] oidc - url redirect: {redirect_url}")
        logger.debug(f"[auth] oidc - endpoint authorize: {self.url_authorize}")
        logger.debug(f"[auth] oidc - endpoint token: {self.url_oauthtoken}")
        logger.debug(f"[auth] oidc - path: {host_url_path}")
        logger.debug(f"[auth] oidc - auth authorized routes: {auth_authorized_routes}")
        logger.debug(f"[auth] oidc - auth authorized prefix paths: {auth_authorized_prefix_paths}")
        self.authlib = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope.split(" "),
            redirect_uri=redirect_url,
            authorization_endpoint=self.url_authorize,
            token_endpoint=self.url_oauthtoken,
        )

        self.unauthorized_action = unauthorized_action
        self.callback_func = callback

        @asgi_app.middleware("http")
        async def oidc_middleware(request: Request, call_next):
            session = request.cookies.get('session')

            is_one_of_url_prefix_allowed = any(request.url.path.startswith(url_prefix) for url_prefix in auth_authorized_prefix_paths)
            if session is not None or request.url.path in auth_authorized_routes or is_one_of_url_prefix_allowed:
                response: Response = await call_next(request)
                return response
            else:
                url = self.authlib.create_authorization_url(self.url_authorize)
                response = RedirectResponse(url=url[0])
                return response

        @asgi_app.get('/' + urlstrip(self.callback_authorize))
        async def route_callback(request: Request):
            self.authlib.fetch_token(url=self.url_oauthtoken, authorization_response=str(request.url))
            try:
                host_url_path = urlpath(self.host_url)
                response = RedirectResponse(url=host_url_path)
                session_id = session_manager.generate_session_id()

                app_runner = writer.serve.app_runner(asgi_app)
                await app_runner.init_session(InitSessionRequestPayload(
                    cookies=request.cookies, headers=request.headers, proposedSessionId=session_id))

                userinfo = {}
                if self.url_userinfo:
                    userinfo = self.authlib.get(self.url_userinfo).json()

                if self.callback_func:
                    self.callback_func(request, session_id, userinfo)

                if self.url_userinfo:
                    app_runner.set_userinfo(session_id=session_id, userinfo=userinfo)

                response.set_cookie(key="session", value=session_id, httponly=True)
                return response
            except Unauthorized as exc:
                if self.unauthorized_action is not None:
                    return self.unauthorized_action(request, exc)
                else:
                    templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
                    return templates.TemplateResponse(request=request, name="auth_unauthorized.html", status_code=exc.status_code, context={
                        "status_code": exc.status_code,
                        "message": exc.message,
                        "more_info": exc.more_info
                    })


def Google(client_id: str, client_secret: str, host_url: str, app_static_public = False) -> Oidc:
    """
    Configure Google Social login configured through Client Id for Web application in Google Cloud Console.

    >>> import writer.auth
    >>> oidc = writer.auth.Google(client_id="xxxxxxx", client_secret="xxxxxxxxxxxxx.apps.googleusercontent.com", host_url="http://localhost:5000")

    :param client_id: client id of Web application
    :param client_secret: client secret of Web application
    :param host_url: The URL of the Writer Framework application (for callback)
    :param app_static_public: authorizes the exposure of the user's static assets (/static and /extensions)
    """
    return Oidc(
        client_id=client_id,
        client_secret=client_secret,
        host_url=host_url,
        url_authorize="https://accounts.google.com/o/oauth2/auth",
        url_oauthtoken="https://oauth2.googleapis.com/token",
        url_userinfo="https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
        app_static_public=app_static_public
    )

def Github(client_id: str, client_secret: str, host_url: str, app_static_public = False) -> Oidc:
    """
    Configure Github authentication.

    >>> import writer.auth
    >>> oidc = writer.auth.Github(client_id="xxxxxxx", client_secret="xxxxxxxxxxxxx", host_url="http://localhost:5000")

    :param client_id: client id
    :param client_secret: client secret
    :param host_url: The URL of the Writer Framework application (for callback)
    :param app_static_public: authorizes the exposure of the user's static assets (/static and /extensions)
    """

    return Oidc(
        client_id=client_id,
        client_secret=client_secret,
        host_url=host_url,
        url_authorize="https://github.com/login/oauth/authorize",
        url_oauthtoken="https://github.com/login/oauth/access_token",
        url_userinfo="https://api.github.com/user",
        app_static_public=app_static_public
    )

def Auth0(client_id: str, client_secret: str, domain: str, host_url: str, app_static_public = False) -> Oidc:
    """
    Configure Auth0 application for authentication.

    >>> import writer.auth
    >>> oidc = writer.auth.Auth0(client_id="xxxxxxx", client_secret="xxxxxxxxxxxxx", domain="xxx-xxxxx.eu.auth0.com", host_url="http://localhost:5000")

    :param client_id: client id
    :param client_secret: client secret
    :param domain: Domain of the Auth0 application
    :param host_url: The URL of the Writer Framework application (for callback)
    :param app_static_public: authorizes the exposure of the user's static assets (/static and /extensions)
    """

    return Oidc(
        client_id=client_id,
        client_secret=client_secret,
        host_url=host_url,
        url_authorize=f"https://{domain}/authorize",
        url_oauthtoken=f"https://{domain}/oauth/token",
        url_userinfo=f"https://{domain}/userinfo",
        app_static_public=app_static_public
    )

def urlpath(url: str):
    """
    >>> urlpath("http://localhost/app1")
    >>> "/app1"

    >>> urlpath("http://localhost")
    >>> "/"
    """
    path = urlparse(url).path
    if len(path) == 0:
        return "/"
    else:
        return path

def urljoin(*args):
    """
    >>> urljoin("http://localhost/app1", "edit")
    >>> "http://localhost/app1/edit"

    >>> urljoin("app1/", "edit")
    >>> "app1/edit"

    >>> urljoin("app1", "edit")
    >>> "app1/edit"

    >>> urljoin("/app1/", "/edit")
    >>> "/app1/edit"
    """
    root_part = args[0]
    root_part_is_root_path = root_part.startswith('/') and len(root_part) > 1

    url_strip_parts = []
    for part in args:
        if part:
            url_strip_parts.append(urlstrip(part))

    return '/'.join(url_strip_parts) if root_part_is_root_path is False else '/' + '/'.join(url_strip_parts)

def urlstrip(url_path: str):
    """

    >>> urlstrip("/app1/")
    >>> "app1"

    >>> urlstrip("http://localhost/app1")
    >>> "http://localhost/app1"

    >>> urlstrip("http://localhost/app1/")
    >>> "http://localhost/app1"
    """
    return url_path.strip('/')

def _client_ip(request: Request) -> str:
    """
    Get the client IP address from the request.

    >>> _client_ip(request)
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # X-Forwarded-For can contain a list of IPs, the first is the real IP of the client
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        # Otherwise, use the direct connection IP
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip is not None:
            ip = x_real_ip
        else:
            client = request.client
            ip = client.host if client is not None else ""

    return ip
