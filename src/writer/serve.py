import asyncio
import importlib.util
import logging
import mimetypes
import os
import os.path
import pathlib
import socket
import textwrap
import typing
from contextlib import asynccontextmanager
from importlib.machinery import ModuleSpec
from typing import Any, Callable, Dict, List, Literal, Optional, Set, Tuple, Union, cast
from urllib.parse import urlsplit

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.routing import Mount
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from writer import VERSION, abstract
from writer.app_runner import AppRunner
from writer.ss_types import (
    AppProcessServerResponse,
    ComponentUpdateRequestPayload,
    EventResponsePayload,
    InitRequestBody,
    InitResponseBodyEdit,
    InitResponseBodyRun,
    InitSessionRequestPayload,
    InitSessionResponsePayload,
    ServeMode,
    StateEnquiryResponsePayload,
    WriterEvent,
    WriterWebsocketIncoming,
    WriterWebsocketOutgoing,
)

if typing.TYPE_CHECKING:
    from .auth import Auth, Unauthorized

MAX_WEBSOCKET_MESSAGE_SIZE = 201*1024*1024
logging.getLogger().setLevel(logging.INFO)


class WriterState(typing.Protocol):
    app_runner: AppRunner
    writer_app: bool
    is_server_static_mounted: bool

class WriterAsgi(typing.Protocol):
    state: WriterState

class WriterFastAPI(FastAPI, WriterAsgi):  # type: ignore
    pass

app: WriterFastAPI = cast(WriterFastAPI, None)

def get_asgi_app(
        user_app_path: str,
        serve_mode: ServeMode,
        enable_remote_edit: bool = False,
        enable_server_setup: bool = True,
        on_load: Optional[Callable] = None,
        on_shutdown: Optional[Callable] = None,
) -> WriterFastAPI:
    """
    Builds an ASGI server that can be injected into another ASGI application
    or an asgi server like uvicorn

    >>> asgi_app = writer.serve.get_asgi_app("app1", "run")
    >>> uvicorn.run(asgi_app, host="0.0.0.0", port=5328)

    :param user_app_path: writer application path
    :param serve_mode: server mode (run, edit)
    :param enable_remote_edit: allow editing from the internet (by default, editing only works locally)
    :param enable_server_setup: enables fastapi setup hook on startup, server_setup.py
    :param on_load: callback called on loading
    :param on_shutdown: callback called at shutdown
    :return: ASGI Server
    """
    global app
    if serve_mode not in ["run", "edit"]:
        raise ValueError("""Invalid mode. Must be either "run" or "edit".""")

    _fix_mimetype()
    app_runner = AppRunner(user_app_path, serve_mode)

    @asynccontextmanager
    async def lifespan(asgi_app: FastAPI):
        nonlocal app_runner

        app_runner.hook_to_running_event_loop()
        app_runner.load()

        if on_load is not None \
           and hasattr(asgi_app.state, 'is_server_static_mounted') \
           and asgi_app.state.is_server_static_mounted:
            on_load()

        try:
            yield
        except asyncio.CancelledError:
            pass

        app_runner.shut_down()
        if on_shutdown is not None:
            on_shutdown()

    app = cast(WriterFastAPI, FastAPI(lifespan=lifespan))
    """
    Reuse the same pattern to give variable to FastAPI application
    than `app.state.is_server_static_mounted` already use in Writer Framework.
    """
    app.state.writer_app = True
    app.state.app_runner = app_runner

    def _get_extension_paths() -> List[str]:
        extensions_path = pathlib.Path(user_app_path) / "extensions"
        if not extensions_path.exists():
            return []
        filtered_files = [f for f in extensions_path.rglob(
            "*") if f.suffix.lower() in (".js", ".css") and f.is_file()]
        relative_paths = [f.relative_to(
            extensions_path).as_posix() for f in filtered_files]
        return relative_paths

    cached_extension_paths = _get_extension_paths()

    def _check_origin_header(origin_header: Optional[str]) -> bool:
        if serve_mode not in ("edit") or enable_remote_edit is True:
            return True
        if origin_header is None:
            return False
        hostname = urlsplit(origin_header).hostname
        if hostname in ("127.0.0.1", "localhost"):
            return True
        return False

    # Init

    def _get_run_starter_pack(payload: InitSessionResponsePayload):
        return InitResponseBodyRun(
            mode="run",
            sessionId=payload.sessionId,
            userState=payload.userState,
            mail=payload.mail,
            components=payload.components,
            userFunctions=payload.userFunctions,
            extensionPaths=cached_extension_paths,
            featureFlags=payload.featureFlags,
            abstractTemplates=abstract.templates
        )

    def _get_edit_starter_pack(payload: InitSessionResponsePayload):
        run_code: Optional[str] = app_runner.run_code

        return InitResponseBodyEdit(
            mode="edit",
            sessionId=payload.sessionId,
            userState=payload.userState,
            mail=payload.mail,
            components=payload.components,
            userFunctions=payload.userFunctions,
            runCode=run_code,
            extensionPaths=cached_extension_paths,
            featureFlags=payload.featureFlags,
            abstractTemplates=abstract.templates
        )

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    @app.post("/api/init")
    async def init(initBody: InitRequestBody, request: Request, response: Response) -> Union[InitResponseBodyRun, InitResponseBodyEdit]:

        """
        Handles session init and provides a "starter pack" to the frontend.
        """

        origin_header = request.headers.get("origin")
        if not _check_origin_header(origin_header):
            wrong_origin_message = "A session request with origin %s was rejected. For security reasons, only local origins are allowed in edit mode. "
            wrong_origin_message += "To circumvent this protection, use the --enable-remote-edit flag if running via command line."
            logging.error(wrong_origin_message, origin_header)
            raise HTTPException(
                status_code=403, detail="Incorrect origin. Only local origins are allowed.")

        session_id = request.cookies.get("session")
        if session_id is not None:
            initBody.proposedSessionId = session_id


        app_response = await app_runner.init_session(InitSessionRequestPayload(
            cookies=dict(request.cookies),
            headers=dict(request.headers),
            proposedSessionId=initBody.proposedSessionId
        ))

        status = app_response.status

        """
        Deletes the session cookie that was set by 
        authentication when it is present.
        """
        if session_id is not None:
            response.delete_cookie("session")

        if status == "error" or app_response.payload is None:
            raise HTTPException(status_code=403, detail="Session rejected.")

        if serve_mode == "run":
            return _get_run_starter_pack(app_response.payload)

        if serve_mode == "edit":
            return _get_edit_starter_pack(app_response.payload)


    # Streaming

    async def _stream_session_init(websocket: WebSocket):

        """
        Waits for the client to provide a session id to initialise the stream.
        Returns the session id received.
        """

        session_id = None
        while session_id is None:
            req_message_raw = await websocket.receive_json()

            try:
                req_message = WriterWebsocketIncoming.model_validate(
                    req_message_raw)
            except ValidationError:
                logging.error("Incorrect incoming request.")
                return

            if req_message.type == "streamInit" and req_message.payload is not None:
                session_id = req_message.payload.get("sessionId")
        return session_id

    async def _stream_incoming_requests(websocket: WebSocket, session_id: str):

        """
        Handles incoming requests from client. 
        """

        pending_tasks: Set[asyncio.Task] = set()

        try:
            while True:
                req_message_raw = await websocket.receive_json()

                try:
                    req_message = WriterWebsocketIncoming.model_validate(
                        req_message_raw)
                except ValidationError:
                    logging.error("Incorrect incoming request.")
                    break

                is_session_ok = await app_runner.check_session(session_id)
                if not is_session_ok:
                    break

                new_task = None

                if req_message.type == "event":
                    new_task = asyncio.create_task(
                        _handle_incoming_event(websocket, session_id, req_message))
                elif req_message.type == "keepAlive":
                    new_task = asyncio.create_task(
                        _handle_keep_alive_message(websocket, session_id, req_message))
                elif req_message.type == "stateEnquiry":
                    new_task = asyncio.create_task(
                        _handle_state_enquiry_message(websocket, session_id, req_message))
                elif serve_mode == "edit":
                    new_task = asyncio.create_task(
                        _handle_incoming_edit_message(websocket, session_id, req_message))

                if new_task:
                    pending_tasks.add(new_task)
                    new_task.add_done_callback(pending_tasks.discard)
        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            raise
        finally:
            # Cancel pending tasks

            for pending_task in pending_tasks.copy():
                pending_task.cancel()
                try:
                    await pending_task
                except asyncio.CancelledError:
                    pass

    async def _handle_incoming_event(websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming):
        response = WriterWebsocketOutgoing(
            messageType=f"{req_message.type}Response",
            trackingId=req_message.trackingId,
            payload=None
        )
        res_payload: Optional[Dict[str, Any]] = None
        apsr: Optional[AppProcessServerResponse] = None
        apsr = await app_runner.handle_event(
            session_id, WriterEvent(
                type=req_message.payload["type"],
                instancePath=req_message.payload["instancePath"],
                payload=req_message.payload["payload"]
            ))
        if apsr is not None and apsr.payload is not None:
            res_payload = typing.cast(
                EventResponsePayload, apsr.payload).model_dump()
        if res_payload is not None:
            response.payload = res_payload
        await websocket.send_json(response.model_dump())

    async def _handle_incoming_edit_message(websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming):
        response = WriterWebsocketOutgoing(
            messageType=f"{req_message.type}Response",
            trackingId=req_message.trackingId,
            payload=None
        )
        if req_message.type == "componentUpdate":
            await app_runner.update_components(
                session_id, ComponentUpdateRequestPayload(
                    components=req_message.payload["components"]
                ))
        elif req_message.type == "codeSaveRequest":
            app_runner.save_code(
                session_id, req_message.payload["code"])
        elif req_message.type == "codeUpdate":
            app_runner.update_code(
                session_id, req_message.payload["code"])
        await websocket.send_json(response.model_dump())

    async def _handle_keep_alive_message(websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming):
        response = WriterWebsocketOutgoing(
            messageType="keepAliveResponse",
            trackingId=req_message.trackingId,
            payload=None
        )
        await websocket.send_json(response.model_dump())

    async def _handle_state_enquiry_message(websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming):
        response = WriterWebsocketOutgoing(
            messageType=f"{req_message.type}Response",
            trackingId=req_message.trackingId,
            payload=None
        )
        res_payload: Optional[Dict[str, Any]] = None
        apsr: Optional[AppProcessServerResponse] = None
        apsr = await app_runner.handle_state_enquiry(session_id)
        if apsr is not None and apsr.payload is not None:
            res_payload = typing.cast(
                StateEnquiryResponsePayload, apsr.payload).model_dump()
        if res_payload is not None:
            response.payload = res_payload
        await websocket.send_json(response.model_dump())

    async def _stream_outgoing_announcements(websocket: WebSocket):

        """
        Handles outgoing communications to client (announcements).
        """

        if app_runner.code_update_condition is None:
            raise ValueError("Code update condition not set.")

        await app_runner.code_update_condition.acquire()
        try:
            await app_runner.code_update_condition.wait()
        finally:
            app_runner.code_update_condition.release()

        announcement = WriterWebsocketOutgoing(
            messageType="announcement",
            trackingId=-1,
            payload={
                "announce": "codeUpdate"
            }
        )

        if websocket.application_state == WebSocketState.DISCONNECTED:
            return

        try:
            await websocket.send_json(announcement.dict())
        except (WebSocketDisconnect):
            pass

    @app.websocket("/api/stream")
    async def stream(websocket: WebSocket):

        """ Initialises incoming and outgoing communications on the stream. """

        await websocket.accept()

        origin_header = websocket.headers.get("origin")
        if not _check_origin_header(origin_header):
            await websocket.close(code=1008)
            return

        try:
            session_id = await _stream_session_init(websocket)
        except WebSocketDisconnect:
            return

        is_session_ok = await app_runner.check_session(session_id)
        if not is_session_ok:
            await websocket.close(code=1008)  # Invalid permissions
            return

        task1 = asyncio.create_task(
            _stream_incoming_requests(websocket, session_id))
        task2 = asyncio.create_task(_stream_outgoing_announcements(websocket))

        try:
            await asyncio.wait((task1, task2), return_when=asyncio.FIRST_COMPLETED)
            await asyncio.sleep(1)
            task1.cancel()
            task2.cancel()
            await task1
            await task2
        except asyncio.CancelledError:
            pass

    # Mount static paths

    user_app_static_path = pathlib.Path(user_app_path) / "static"
    if user_app_static_path.exists():
        app.mount(
            "/static", StaticFiles(directory=str(user_app_static_path)), name="user_static")

    user_app_extensions_path = pathlib.Path(user_app_path) / "extensions"
    if user_app_extensions_path.exists():
        app.mount(
            "/extensions", StaticFiles(directory=str(user_app_extensions_path)), name="extensions")

    server_path = pathlib.Path(__file__)
    server_static_path = server_path.parent / "static"
    if server_static_path.exists():
        _mount_server_static_path(app, server_static_path)
        app.state.is_server_static_mounted = True
    else:
        logging.error(
            textwrap.dedent(
                """\
                \x1b[31;20mError: Failed to acquire server static path. Writer Framework may not be properly built.

                To resolve this issue, try the following steps:
                1. Run the 'npm run build' script in the 'ui' directory and then restart the app.
                2. Alternatively, launch a UI instance by running 'npm run dev' in the 'ui' directory.

                Please refer to the CONTRIBUTING.md for detailed instructions.\x1b[0m"""
            )
        )

    # Return
    if enable_server_setup is True:
        _execute_server_setup_hook(user_app_path)

    return app


def print_init_message():
    print(f"""               
                                                               
                   &@@@@@@@@@@     ,@@@@@@@@@@*     @@@@@@@@@@                  
                   .@@@@@@@@@@(     &@@@@@@@@@@     *@@@@@@@@*                  
                    %@@@@@@@@@@     .@@@@@@@@@@(     @@@@@@@@                   
                     @@@@@@@@@@&     #@@@@@@@@@@      @@@@@@                    
                     ,@@@@@@@@@@,     @@@@@@@@@@@     (@@@@(                    
                      &@@@@@@@@@@     .@@@@@@@@@@*     @@@@                     
                       @@@@@@@@@@%     %@@@@@@@@@@     .@@,                     
                       (@@@@@@@@@@.     @@@@@@@@@@%     %&                      
                        @@@@@@@@@@&     (@@@@@@@@@@      .                      
                        *@@@@@@@@@@,     @@@@@@@@@@&                            
                         @@@@@@@@@@@     ,@@@@@@@@@@*                           
                          @@@@@@@@@@#     %@@@@@@@@@@ 


WRITER FRAMEWORK v{VERSION}""")


def print_route_message(run_name: str, port: int, host: str):
    GREEN_TOKEN = "\033[92m"
    END_TOKEN = "\033[0m"

    print(f"{run_name} is available at:{END_TOKEN}{GREEN_TOKEN} http://{host}:{port}{END_TOKEN}", flush=True)

def register_auth(
    auth: 'Auth',
    callback: Optional[Callable[[Request, str, dict], None]] = None,
    unauthorized_action: Optional[Callable[[Request, 'Unauthorized'], Response]] = None
):
    auth.register(app, callback=callback, unauthorized_action=unauthorized_action)

def serve(app_path: str, mode: ServeMode, port: Optional[int], host, enable_remote_edit=False, enable_server_setup=False):
    """ Initialises the web server. """

    print_init_message()

    def on_load():
        run_name = "Builder" if mode == "edit" else "App"
        print_route_message(run_name, port, host)

    """
    Loading of the server_setup.py is active by default 
    when Writer Framework is launched with the run command.
    """
    if port is None:
        mode_allowed_ports = {
            'run': (3005, 3099),
            'edit': (4005, 4099)
        }

        port = _next_localhost_available_port(mode_allowed_ports[mode])

    enable_server_setup = mode == "run" or enable_server_setup
    app = get_asgi_app(app_path, mode, enable_remote_edit, on_load=on_load, enable_server_setup=enable_server_setup)
    log_level = "warning"
    uvicorn.run(app, host=host, port=port, log_level=log_level, ws_max_size=MAX_WEBSOCKET_MESSAGE_SIZE)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This feature supports launching multiple Writer Framework applications simultaneously.

    >>> import uvicorn
    >>> import writer.serve
    >>> from fastapi import FastAPI, Response
    >>>
    >>> root_asgi_app = FastAPI(lifespan=writer.serve.lifespan)
    >>>
    >>> sub_asgi_app_1 = writer.serve.get_asgi_app("../app1", "run")
    >>> sub_asgi_app_2 = writer.serve.get_asgi_app("../app2", "run")
    >>>
    >>> uvicorn.run(root_asgi_app, ws_max_size=writer.serve.MAX_WEBSOCKET_MESSAGE_SIZE)

    Writer Framework uses lifespan to start an application server (app_runner) per
    application.
    """
    writer_lifespans = []
    for route in app.routes:
        if isinstance(route, Mount) and isinstance(route.app, FastAPI):
            if hasattr(route.app.state, "writer_app"):
                ctx = route.app.router.lifespan_context
                writer_lifespans.append(ctx)

    async with _lifespan_invoke(writer_lifespans, app):
        yield


@asynccontextmanager
async def _lifespan_invoke(context: list, app: FastAPI):
    """
    Helper to run multiple lifespans in cascade.

    Running

    >>> _lifespan_invoke([app1.router.lifespan_context, app2.router.lifespan_context], app)

    is equivalent to

    >>> @asynccontextmanager
    >>> async def lifespan_context(app: FastAPI):
    >>>   async with app1.router.lifespan_context(app):
    >>>     async with app2.router.lifespan_context(app):
    >>>       yield
    """
    ctx = context.pop(0)
    async with ctx(app):
        if len(context) > 0:
            async with _lifespan_invoke(context, app):
                yield
        else:
            yield

def _fix_mimetype():
    """
    Fixes mimetypes for .js files. This is needed for the webserver to serve .js files correctly.
    """
    js_mimetype = mimetypes.guess_type("myfile.js")[0]
    if js_mimetype[0] != "text/javascript":
        mimetypes.add_type("text/javascript", ".js")

def _mount_server_static_path(app: FastAPI, server_static_path: pathlib.Path) -> None:
    """
    Unitarily declares the files and folders present in "/static" directory of source code.

    We avoid the general declaration as below. This declaration limit the ability of a developper to
    declare it's own route.
    
    >>> asgi_app.mount("/", StaticFiles(directory=str(server_static_path), html=True), name="server_static")

    Writer Framework routes remain priority. A developer cannot come and overload them.
    """
    app.get('/')(lambda: FileResponse(server_static_path.joinpath('index.html')))
    for f in wf_root_static_assets():
        if f.is_file():
            app.get(f"/{f.name}")(lambda: FileResponse(f))
        if f.is_dir():
            app.mount(f"/{f.name}", StaticFiles(directory=f), name=f"server_static_{f}")


def app_runner(asgi_app: WriterFastAPI) -> AppRunner:
    return asgi_app.state.app_runner


def wf_root_static_assets() -> List[pathlib.Path]:
    """
    Lists the root writer Framework static assets. Some of them are files, some other are directories.

    >>> for f in wf_root_static_assets()
    >>>     print(f"{f.name}")
    >>>     # favicon.ico
    >>>     # assets

    """
    all_static_assets: List[pathlib.Path] = []
    server_path = pathlib.Path(__file__)
    server_static_path = server_path.parent / "static"
    for f in server_static_path.glob('*'):
        all_static_assets.append(f)

    return all_static_assets


def _execute_server_setup_hook(user_app_path: str) -> None:
    """
    Runs the server_setup.py module if present in the application directory.

    """
    server_setup_path = os.path.join(user_app_path, "server_setup.py")
    if os.path.isfile(server_setup_path):
        spec = cast(ModuleSpec, importlib.util.spec_from_file_location("server_setup", server_setup_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore


def _next_localhost_available_port(port_range: Tuple[int, int]) -> int:
    """
    Searches for a free port in a given range on localhost to start the server

    >>> port = _next_localhost_available_port((3005, 3099))

    3005 is the first port to be tested. If it is not available, the port 3006 is tested, and so on.
    """
    for port in range(port_range[0], port_range[1]):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result != 0:
            return port

    raise OSError(f"No free port found to start the server between {port_range[0]} and {port_range[1]} .")
