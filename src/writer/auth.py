import dataclasses
import os.path
from abc import ABCMeta, abstractmethod
from typing import Callable, Optional
from urllib.parse import urlparse

from authlib.integrations.requests_client.oauth2_session import OAuth2Session  # type: ignore
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import writer.serve
from writer.core import session_manager
from writer.serve import WriterFastAPI
from writer.ss_types import InitSessionRequestPayload


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
                 app: WriterFastAPI,
                 callback: Optional[Callable[[Request, str, dict], None]] = None,
                 unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None
    ):
        raise NotImplementedError


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

    authlib: OAuth2Session = None
    callback_func: Optional[Callable[[Request, str, dict], None]] = None # Callback to validate user authentication
    unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None # Callback to build its own page when a user is not allowed


    def register(self,
                 asgi_app: WriterFastAPI,
                 callback: Optional[Callable[[Request, str, dict], None]] = None,
                 unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None
                 ):
        self.authlib = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope.split(" "),
            redirect_uri=_urljoin(self.host_url, self.callback_authorize),
            authorization_endpoint=self.url_authorize,
            token_endpoint=self.url_oauthtoken,
        )

        self.callback_func = callback

        @asgi_app.middleware("http")
        async def oidc_middleware(request: Request, call_next):
            session = request.cookies.get('session')
            host_url_path = _urlpath(self.host_url)
            full_callback_authorize = '/' + _urljoin(host_url_path, self.callback_authorize)
            full_assets = '/' + _urljoin(host_url_path, '/assets')
            if session is not None or request.url.path in [full_callback_authorize] or request.url.path.startswith(full_assets):
                response: Response = await call_next(request)
                return response
            else:
                url = self.authlib.create_authorization_url(self.url_authorize)
                response = RedirectResponse(url=url[0])
                return response

        @asgi_app.get('/' + _urlstrip(self.callback_authorize))
        async def route_callback(request: Request):
            self.authlib.fetch_token(url=self.url_oauthtoken, authorization_response=str(request.url))
            try:
                host_url_path = _urlpath(self.host_url)
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


def Google(client_id: str, client_secret: str, host_url: str) -> Oidc:
    """
    Configure Google Social login configured through Client Id for Web application in Google Cloud Console.

    >>> import writer.auth
    >>> oidc = writer.auth.Google(client_id="xxxxxxx", client_secret="xxxxxxxxxxxxx.apps.googleusercontent.com", host_url="http://localhost:5000")

    :param client_id: client id of Web application
    :param client_secret: client secret of Web application
    :param host_url: The URL of the Writer Framework application (for callback)
    """
    return Oidc(
        client_id=client_id,
        client_secret=client_secret,
        host_url=host_url,
        url_authorize="https://accounts.google.com/o/oauth2/auth",
        url_oauthtoken="https://oauth2.googleapis.com/token",
        url_userinfo="https://www.googleapis.com/oauth2/v1/userinfo?alt=json")

def Github(client_id: str, client_secret: str, host_url: str) -> Oidc:
    """
    Configure Github authentication.

    >>> import writer.auth
    >>> oidc = writer.auth.Github(client_id="xxxxxxx", client_secret="xxxxxxxxxxxxx", host_url="http://localhost:5000")

    :param client_id: client id
    :param client_secret: client secret
    :param host_url: The URL of the Writer Framework application (for callback)
    """
    return Oidc(
        client_id=client_id,
        client_secret=client_secret,
        host_url=host_url,
        url_authorize="https://github.com/login/oauth/authorize",
        url_oauthtoken="https://github.com/login/oauth/access_token",
        url_userinfo="https://api.github.com/user")

def Auth0(client_id: str, client_secret: str, domain: str, host_url: str) -> Oidc:
    """
    Configure Auth0 application for authentication.

    >>> import writer.auth
    >>> oidc = writer.auth.Auth0(client_id="xxxxxxx", client_secret="xxxxxxxxxxxxx", domain="xxx-xxxxx.eu.auth0.com", host_url="http://localhost:5000")

    :param client_id: client id
    :param client_secret: client secret
    :param domain: Domain of the Auth0 application
    :param host_url: The URL of the Writer Framework application (for callback)
    """
    return Oidc(
        client_id=client_id,
        client_secret=client_secret,
        host_url=host_url,
        url_authorize=f"https://{domain}/authorize",
        url_oauthtoken=f"https://{domain}/oauth/token",
        url_userinfo=f"https://{domain}/userinfo")

def _urlpath(url: str):
    """
    >>> _urlpath("http://localhost/app1")
    >>> "/app1"
    """
    return urlparse(url).path

def _urljoin(*args):
    """
    >>> _urljoin("http://localhost/app1", "edit")
    >>> "http://localhost/app1/edit"

    >>> _urljoin("app1/", "edit")
    >>> "app1/edit"

    >>> _urljoin("app1", "edit")
    >>> "app1/edit"

    >>> _urljoin("/app1/", "/edit")
    >>> "app1/edit"
    """
    url_strip_parts = []
    for part in args:
        if part:
            url_strip_parts.append(_urlstrip(part))

    return '/'.join(url_strip_parts)

def _urlstrip(url_path: str):
    """

    >>> _urlstrip("/app1/")
    >>> "app1"

    >>> _urlstrip("http://localhost/app1")
    >>> "http://localhost/app1"

    >>> _urlstrip("http://localhost/app1/")
    >>> "http://localhost/app1"
    """
    return url_path.strip('/')
