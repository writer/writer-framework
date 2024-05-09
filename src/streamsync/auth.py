import dataclasses
import os.path
from abc import ABCMeta, abstractmethod
from typing import Callable, Optional

from authlib.integrations.requests_client.oauth2_session import OAuth2Session  # type: ignore
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import streamsync.serve
from streamsync.core import session_manager
from streamsync.serve import StreamsyncFastAPI
from streamsync.ss_types import InitSessionRequestPayload


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
    Interface to implement authentication in streamsync.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def register(self,
                 app: StreamsyncFastAPI,
                 callback: Optional[Callable[[Request, str, dict], None]] = None,
                 unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None
    ):
        raise NotImplementedError


@dataclasses.dataclass
class Oidc(Auth):
    """
    Configure streamsync to use OpenID Connect. If this is set, streamsync will
    redirect anonymous users to OpenID Connect issuer.

    The issuer will then
    authenticate the user and redirect back to the streamsync application with
    an authorization code. The streamsync application will then exchange the
    authorization code for an access token and use the access token to
    authenticate the user and fetch user information.

    >>> oidc = Oidc(
    ...     client_id="xxxxxxx",
    ...     client_secret="xxxxxxxxxxxxx.apps.googleusercontent.com",
    ...     url_authorize="https://accounts.google.com/o/oauth2/auth",
    ...     url_oauthtoken="https://oauth2.googleapis.com/token",
    ...     url_userinfo="https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
    ... )
    >>> streamsync.server.register_auth(oidc)

    """
    client_id: str
    client_secret: str
    host_url: str
    url_authorize: str
    url_oauthtoken: str
    scope: str = "openid email profile"
    callback_route: str = "/callback"
    url_userinfo: Optional[str] = None

    authlib: OAuth2Session = None
    callback_func: Optional[Callable[[Request, str, dict], None]] = None # Callback to validate user authentication
    unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None # Callback to build its own page when a user is not allowed


    def register(self,
                 asgi_app: StreamsyncFastAPI,
                 callback: Optional[Callable[[Request, str, dict], None]] = None,
                 unauthorized_action: Optional[Callable[[Request, Unauthorized], Response]] = None
                 ):
        self.authlib = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope.split(" "),
            redirect_uri=f"{self.host_url}{self.callback_route}",
            authorization_endpoint=self.url_authorize,
            token_endpoint=self.url_oauthtoken,
        )

        self.callback_func = callback

        @asgi_app.middleware("http")
        async def oidc_middleware(request: Request, call_next):
            session = request.cookies.get('session')
            if session is not None or request.url.path in [self.callback_route] or request.url.path.startswith('/assets'):
                return await call_next(request)
            else:
                url = self.authlib.create_authorization_url(self.url_authorize)
                response = RedirectResponse(url=url[0])
                return response

        @asgi_app.get(self.callback_route)
        async def route_callback(request: Request):
            self.authlib.fetch_token(url=self.url_oauthtoken, authorization_response=str(request.url))
            try:
                response = RedirectResponse(url='/')
                session_id = session_manager.generate_session_id()

                app_runner = streamsync.serve.app_runner(asgi_app)
                await app_runner.init_session(InitSessionRequestPayload(
                    cookies=request.cookies, headers=request.headers, proposedSessionId=session_id))

                userinfo = {}
                if self.url_userinfo:
                    userinfo = self.authlib.get(self.url_userinfo).json()
                    app_runner.set_userinfo(session_id=session_id, userinfo=userinfo)

                if self.callback_func:
                    self.callback_func(request, session_id, userinfo)

                response.set_cookie(key="session", value=session_id, httponly=True, expires=0)
                return response
            except Unauthorized as exc:
                if self.unauthorized_action:
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

    >>> import streamsync.auth
    >>> oidc = streamsync.auth.Google(client_id="xxxxxxx", client_secret="xxxxxxxxxxxxx.apps.googleusercontent.com", host_url="http://localhost:5000")

    :param client_id: client id of Web application
    :param client_secret: client secret of Web application
    :param host_url: The URL of the streamsync application (for callback)
    """
    return Oidc(
        client_id=client_id,
        client_secret=client_secret,
        host_url=host_url,
        url_authorize="https://accounts.google.com/o/oauth2/auth",
        url_oauthtoken="https://oauth2.googleapis.com/token",
        url_userinfo="https://www.googleapis.com/oauth2/v1/userinfo?alt=json")

def Auth0(client_id: str, client_secret: str, domain: str, host_url: str) -> Oidc:
    """
    Configure Auth0 application for authentication.

    >>> import streamsync.auth
    >>> oidc = streamsync.auth.Auth0(client_id="xxxxxxx", client_secret="xxxxxxxxxxxxx", domain="xxx-xxxxx.eu.auth0.com", host_url="http://localhost:5000")

    :param client_id: client id
    :param client_secret: client secret
    :param domain: Domain of the Auth0 application
    :param host_url: The URL of the streamsync application (for callback)
    """
    return Oidc(
        client_id=client_id,
        client_secret=client_secret,
        host_url=host_url,
        url_authorize=f"https://{domain}/authorize",
        url_oauthtoken=f"https://{domain}/oauth/token",
        url_userinfo=f"https://{domain}/userinfo")
