import asyncio
import base64
import html
import importlib.util
import io
import json
import logging
import mimetypes
import os
import os.path
import pathlib
import socket
import tempfile
import textwrap
import time
import typing
from contextlib import asynccontextmanager, suppress
from importlib.machinery import ModuleSpec
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)
from urllib.parse import urlsplit

import orjson
import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.routing import Mount
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from writer import VERSION, abstract
from writer.ai import Graph
from writer.app_runner import AppRunner
from writer.ss_types import (
    AppProcessServerResponse,
    AutogenRequestBody,
    ComponentUpdateRequestPayload,
    EventResponsePayload,
    HashRequestPayload,
    HashRequestResponsePayload,
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

MAX_WEBSOCKET_MESSAGE_SIZE = 201 * 1024 * 1024
BLUEPRINT_API_EXECUTION_TIMEOUT_SECONDS = int(os.getenv("AGENT_BUILDER_BLUEPRINT_API_EXECUTION_TIMEOUT", "600"))
BLUEPRINT_API_RETRY_TIMEOUT = int(os.getenv("AGENT_BUILDER_BLUEPRINT_API_RETRY_TIMEOUT", "10000"))


class WriterState(typing.Protocol):
    app_runner: AppRunner
    writer_app: bool
    is_server_static_mounted: bool
    meta: Union[Dict[str, Any], Callable[[], Dict[str, Any]]]  # meta tags for SEO
    opengraph_tags: Union[
        Dict[str, Any], Callable[[], Dict[str, Any]]
    ]  # opengraph tags for social networks integration (facebook, discord)
    title: Union[str, Callable[[], str]]  # title of the page, default: "Writer Framework"


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
    on_shutdown: Optional[Callable] = None
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
    pending_tasks: Set[asyncio.Task] = set()

    @asynccontextmanager
    async def lifespan(asgi_app: FastAPI):
        nonlocal app_runner

        app_runner.hook_to_running_event_loop()
        app_runner.load()

        if (
            on_load is not None
            and hasattr(asgi_app.state, "is_server_static_mounted")
            and asgi_app.state.is_server_static_mounted
        ):
            on_load()

        try:
            yield
        except asyncio.CancelledError:
            pass

        for pending_task in pending_tasks.copy():
            pending_task.cancel()
            try:
                await pending_task
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
        filtered_files = [
            f
            for f in extensions_path.rglob("*")
            if f.suffix.lower() in (".js", ".css") and f.is_file()
        ]
        relative_paths = [f.relative_to(extensions_path).as_posix() for f in filtered_files]
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
            abstractTemplates=abstract.templates,
            writerApplication=payload.writerApplication,
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
            sourceFiles=app_runner.source_files,
            extensionPaths=cached_extension_paths,
            featureFlags=payload.featureFlags,
            abstractTemplates=abstract.templates,
            writerApplication=payload.writerApplication,
        )

    @app.get("/api/health")
    async def health():
        app_runner = app.state.app_runner
        
        # Check user app process
        if app_runner.app_process is None or not app_runner.app_process.is_alive():
            return JSONResponse(
                status_code=503,
                content={"status": "error", "message": "User app process is not running"}
            )
        
        # Check project saver process (only in edit mode)
        if app_runner.mode == "edit":
            project_saver = app_runner.wf_project_context.write_files_async_process
            if project_saver is None or not project_saver.is_alive():
                return JSONResponse(
                    status_code=503,
                    content={"status": "error", "message": "Project saver process is not running"}
                )
        
        return {"status": "ok"}

    @app.get("/api/export")
    async def export_zip():
        if serve_mode != "edit":
            raise HTTPException(status_code=403, detail="Invalid mode.")
        exported_zip_stream = app_runner.export_zip()
        return StreamingResponse(
            exported_zip_stream,
            media_type="application/x-zip-compressed",
            headers={
                "Content-Disposition": "attachment; filename=exported_agent.zip"
            }
        )

    @app.post("/api/import")
    async def import_zip(file: UploadFile = File(...)):
        if serve_mode != "edit":
            raise HTTPException(status_code=403, detail="Invalid mode.")
        if not file.filename or not file.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="Only .zip files are supported.")

        MAX_FILE_SIZE = 200 * 1024 * 1024

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                # Stream file to disk to avoid memory issues
                size = 0
                while chunk := await file.read(8192):
                    size += len(chunk)
                    if size > MAX_FILE_SIZE:
                        tmp.close()
                        os.unlink(tmp.name)
                        raise HTTPException(status_code=413, detail=f"File too large. Max file size: {MAX_FILE_SIZE}")
                    tmp.write(chunk)
                tmp_path = tmp.name
            await app_runner.import_zip(tmp_path)
            os.remove(tmp_path)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid upload.")

    @app.post("/api/autogen")
    async def autogen(requestBody: AutogenRequestBody, request: Request):
        import writer.autogen
        agent_token_header = request.headers.get('x-agent-token')

        return writer.autogen.generate_blueprint(
            requestBody.description,
            agent_token_header
            )

    @app.post("/api/init")
    async def init(
        initBody: InitRequestBody, request: Request, response: Response
    ) -> Union[InitResponseBodyRun, InitResponseBodyEdit]:
        """
        Handles session init and provides a "starter pack" to the frontend.
        """

        origin_header = request.headers.get("origin")
        if not _check_origin_header(origin_header):
            wrong_origin_message = "A session request with origin %s was rejected. For security reasons, only local origins are allowed in edit mode. "
            wrong_origin_message += "To circumvent this protection, use the --enable-remote-edit flag if running via command line."
            logging.error(wrong_origin_message, origin_header)
            raise HTTPException(
                status_code=403, detail="Incorrect origin. Only local origins are allowed."
            )

        session_id = request.cookies.get("session")
        if session_id is not None:
            initBody.proposedSessionId = session_id

        app_response = await app_runner.init_session(
            InitSessionRequestPayload(
                cookies=dict(request.cookies),
                headers=dict(request.headers),
                proposedSessionId=initBody.proposedSessionId,
            )
        )

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

    # Jobs

    async def _get_payload_as_json(request: Request):
        payload = None
        body = await request.body()
        if not body:
            return None
        try:
            payload = await request.json()
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Cannot parse the payload.")
        return payload
    
    def has_api_trigger(app_runner: AppRunner, blueprint_id: str) -> bool:
        # Check if blueprint has at least one API trigger component
        if not app_runner.bmc_components:
            return False
        return any(
            comp["type"] == "blueprints_apitrigger" and comp.get("parentId") == blueprint_id
            for comp in app_runner.bmc_components.values()
        )

    @app.get("/private/api/blueprints")
    async def get_blueprints(request: Request):
        """
        Returns a list of blueprints available in the agent.
        """
        if not app_runner.bmc_components:
            return JSONResponse(content=[])

        blueprints = [
            {
                "id": comp["id"],
                "key": comp.get("content", {}).get("key")
            }
            for comp in app_runner.bmc_components.values()
            if comp["type"] == "blueprints_blueprint"
            and has_api_trigger(app_runner, comp["id"])
        ]

        return JSONResponse(content=blueprints)

    @app.get("/private/api/cron-triggers")
    async def get_cron_triggers(request: Request):
        """
        Returns a list of Cron Trigger blocks.
        """
        if not app_runner.bmc_components:
            return JSONResponse(content=[], status_code=200)

        cron_triggers = [
            {
                "id": comp.get("id"),
                "blueprint_id": comp.get("parentId"),
                "name": comp.get("name") or comp.get("content", {}).get("name"),
                "cron_expression": comp.get("content", {}).get("cronExpression", ""),
                "timezone": comp.get("content", {}).get("timezone", "UTC"),
            }
            for comp in app_runner.bmc_components.values()
            if comp.get("type") == "blueprints_crontrigger"
        ]

        return JSONResponse(content=cron_triggers, status_code=200)

    @app.post("/private/api/blueprint/{blueprint_id}")
    async def create_blueprint_job(blueprint_id: str, request: Request, response: Response, branch_id: Optional[str] = None):
        # Keep-alive interval for SSE streaming
        KEEPALIVE_INTERVAL = 15
        payload = await _get_payload_as_json(request)

        # --- Session initialization ---

        async def init_session_and_validate(
            app_runner: AppRunner,
            cookies: Dict[str, Any],
            headers: Dict[str, Any],
        ) -> str:
            # Initialize session with passed cookies/headers
            sess_resp = await app_runner.init_session(InitSessionRequestPayload(
                cookies=cookies, headers=headers, proposedSessionId=None
            ))
            if not sess_resp or not sess_resp.payload:
                raise RuntimeError("Cannot initialize session.")
            sid = sess_resp.payload.sessionId
            if not await app_runner.check_session(sid):
                raise RuntimeError("Cannot initialize session.")
            return sid

        # --- Blueprint discovery logic ---

        def check_blueprint(app_runner: AppRunner, blueprint_id: str) -> bool:
            # Locate blueprint component by its key
            if not app_runner.bmc_components:
                return False
            return blueprint_id in app_runner.bmc_components

        # --- Result serialization (recursive) ---

        def serialize_result(data: Any) -> Any:
            # Convert blueprint output into JSON-serializable structure
            if isinstance(data, (str, int, float, bool, type(None))):
                return data
            if isinstance(data, list):
                return [serialize_result(item) for item in data]
            if isinstance(data, dict):
                return {k: serialize_result(v) for k, v in data.items()}
            try:
                return json.loads(json.dumps(data))
            except (TypeError, OverflowError):
                return f"Can't be displayed. Value of type: {type(data)}."

        # --- SSE formatting utilities ---

        async def format_event(event_type: str, data: Dict[str, Any]) -> str:
            # Format a proper Server-Sent Event chunk
            return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

        async def format_keepalive() -> str:
            # Send a SSE comment line as keep-alive (spec compliant)
            return ": keep-alive\n\n"

        # --- The main worker logic that produces events ---

        async def event_logic(queue: asyncio.Queue):
            try:
                await queue.put(await format_event("status", {"status": "in progress", "created_at": int(time.time())}))
                await queue.put(await format_event("status", {"status": "initializing", "msg": "Initializing session..."}))

                # Validate session & credentials
                session_id = await init_session_and_validate(
                    app_runner, dict(request.cookies), dict(request.headers)
                )

                await queue.put(await format_event("status", {"status": "validating", "msg": "Validating blueprint..."}))

                if not app_runner.bmc_components:
                    raise RuntimeError("No blueprints defined in the agent.")

                blueprint_exists = check_blueprint(app_runner, blueprint_id)
                if not blueprint_exists:
                    await queue.put(await format_event("error", {
                        "msg": f"Blueprint '{blueprint_id}' was not found.",
                        "finished_at": int(time.time())
                    }))
                    return

                if not branch_id and not has_api_trigger(app_runner, blueprint_id):
                    await queue.put(await format_event("error", {
                        "msg": f"Blueprint '{blueprint_id}' lacks an API trigger.",
                        "finished_at": int(time.time())
                    }))
                    return

                if branch_id:
                    block = app_runner.bmc_components.get(branch_id)
                    if not block:
                        await queue.put(await format_event("error", {
                            "msg": f"Block '{branch_id}' was not found.",
                            "finished_at": int(time.time())
                        }))
                        return

                await queue.put(await format_event("status", {"status": "executing", "msg": (f"Executing branch: {branch_id}..." if branch_id else f"Executing blueprint: {blueprint_id}...")}))

                if branch_id:
                    task = asyncio.create_task(
                        app_runner.handle_event(
                            session_id,
                            WriterEvent(
                                type="wf-run-blueprint-branch",
                                isSafe=True,
                                handler="run_blueprint_branch",
                                payload={"branch_id": branch_id, **(payload or {})},
                            )
                        )
                    )
                else:
                    task = asyncio.create_task(
                        app_runner.handle_event(
                            session_id,
                            WriterEvent(
                                type="wf-run-blueprint-via-api",
                                isSafe=True,
                                handler="run_blueprint_via_api",
                                payload={"blueprint_id": blueprint_id, **(payload or {})},
                            )
                        )
                    )

                await queue.put(await format_event("status", {"status": "running", "msg": ("Branch is running. Awaiting output..." if branch_id else "Blueprint is running. Awaiting output...")}))

                # Await blueprint execution with timeout protection
                apsr = await asyncio.wait_for(task, timeout=BLUEPRINT_API_EXECUTION_TIMEOUT_SECONDS)

                await queue.put(await format_event("status", {"status": "processing", "msg": "Processing blueprint result..."}))

                if not apsr or apsr.status != "ok":
                    raise RuntimeError("Blueprint execution failed.")

                if apsr.payload and apsr.payload.result:
                    task_status = apsr.payload.result.get("ok", False)
                    result = serialize_result(
                        apsr.payload.result.get("result")
                    )
                else:
                    task_status = False
                    result = "No result returned from blueprint execution."

                if not task_status:
                    await queue.put(await format_event("error", {
                        "msg": result,
                        "finished_at": int(time.time())
                    }))
                else:
                    await queue.put(await format_event("artifact", {
                        "artifact": result,
                        "finished_at": int(time.time())
                    }))

            except Exception as e:
                # Bubble up any unexpected error as 'error' SSE event
                await queue.put(await format_event("error", {
                    "msg": f"Agent Builder internal error: {str(e)}",
                    "finished_at": int(time.time())
                }))
            finally:
                # Always mark stream completion for consumer
                await queue.put("data: [DONE]\n\n")

        # --- The streaming loop that multiplexes events and keep-alives ---

        async def merged_stream() -> AsyncGenerator[str, None]:
            # Type annotation required by mypy
            queue: asyncio.Queue = asyncio.Queue()
            producer_task = asyncio.create_task(event_logic(queue))

            yield f"retry: {BLUEPRINT_API_RETRY_TIMEOUT}\n\n"

            try:
                while True:
                    try:
                        result = await asyncio.wait_for(
                            queue.get(),
                            timeout=KEEPALIVE_INTERVAL
                            )
                        if result == "data: [DONE]\n\n":
                            return
                        yield result
                    except asyncio.TimeoutError:
                        yield await format_keepalive()
                    except asyncio.CancelledError:
                        # Client disconnected, break streaming loop
                        break
            finally:
                # Always cancel producer to prevent orphaned task
                producer_task.cancel()
                with suppress(asyncio.CancelledError):
                    await producer_task

        return StreamingResponse(
            merged_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    # Streaming

    async def _send_json_or_queue(session_id: str, data: Any, websocket: WebSocket):
        try:
            binary_data = orjson.dumps(data)
            await websocket.send_bytes(binary_data)
        except (RuntimeError, WebSocketDisconnect):
            await app_runner.queue_message(session_id, data)

    async def _stream_session_init(websocket: WebSocket):
        """
        Waits for the client to provide a session id to initialise the stream.
        Returns the session id received.
        """

        session_id = None
        while session_id is None:
            req_message_raw = await websocket.receive_json()

            try:
                req_message = WriterWebsocketIncoming.model_validate(req_message_raw)
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

        try:
            while True:
                req_message_raw = await websocket.receive_json()

                try:
                    req_message = WriterWebsocketIncoming.model_validate(req_message_raw)
                except ValidationError:
                    logging.error("Incorrect incoming request.")
                    break

                is_session_ok = await app_runner.check_session(session_id)
                if not is_session_ok:
                    break

                new_task = None

                if req_message.type == "event":
                    new_task = asyncio.create_task(
                        _handle_incoming_event(websocket, session_id, req_message)
                    )
                elif req_message.type == "keepAlive":
                    new_task = asyncio.create_task(
                        _handle_keep_alive_message(websocket, session_id, req_message)
                    )
                elif req_message.type == "stateEnquiry":
                    new_task = asyncio.create_task(
                        _handle_state_enquiry_message(websocket, session_id, req_message)
                    )
                elif serve_mode == "edit" and req_message.type == "hashRequest":
                    new_task = asyncio.create_task(
                        _handle_hash_request(websocket, session_id, req_message)
                    )
                elif serve_mode == "edit":
                    new_task = asyncio.create_task(
                        _handle_incoming_edit_message(websocket, session_id, req_message)
                    )

                if new_task:
                    pending_tasks.add(new_task)
                    new_task.add_done_callback(pending_tasks.discard)
        except WebSocketDisconnect:
            return
        except asyncio.CancelledError:
            raise

    async def _handle_incoming_event(
        websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming
    ):
        response = WriterWebsocketOutgoing(
            messageType=f"{req_message.type}Response",
            trackingId=req_message.trackingId,
            payload=None,
        )

        # Allows for global events if in edit mode (such as "Run blueprint" for previewing a blueprint)

        is_safe = serve_mode == "edit"
        res_payload: Optional[Dict[str, Any]] = None
        apsr: Optional[AppProcessServerResponse] = None
        apsr = await app_runner.handle_event(
            session_id,
            WriterEvent(
                type=req_message.payload.get("type"),
                handler=req_message.payload.get("handler"),
                isSafe=is_safe,
                instancePath=req_message.payload.get("instancePath"),
                payload=req_message.payload.get("payload"),
            ),
        )
        if apsr is not None and apsr.payload is not None:
            res_payload = typing.cast(EventResponsePayload, apsr.payload).model_dump()
        if res_payload is not None:
            response.payload = res_payload
        await _send_json_or_queue(session_id, response.model_dump(), websocket)

    async def _handle_incoming_edit_message(
        websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming
    ):
        response = WriterWebsocketOutgoing(
            messageType=f"{req_message.type}Response",
            trackingId=req_message.trackingId,
            payload=None,
        )
        if req_message.type == "componentUpdate":
            await app_runner.update_components(
                session_id,
                ComponentUpdateRequestPayload(components=req_message.payload["components"]),
            )
            await app_runner.queue_announcement_async(
                "componentUpdate", req_message.payload["components"], session_id
            )
        elif req_message.type == "collaborationPing":
            await app_runner.queue_announcement_async(
                "collaborationUpdate", req_message.payload, exclude_session_id=session_id
            )
        elif req_message.type == "codeSaveRequest":
            app_runner.save_code(
                session_id, req_message.payload["code"], req_message.payload["path"]
            )
        elif req_message.type == "codeUpdate":
            app_runner.update_code(session_id, req_message.payload["code"])
        elif req_message.type == "loadSourceFile":
            path = os.path.join(*req_message.payload["path"])
            try:
                response.payload = {"content": app_runner.load_persisted_script(path)}
            except FileNotFoundError as error:
                logging.warning(f"could not load script at {path}", error)
                response.payload = {"error": str(error)}
        elif req_message.type == "createSourceFile":
            path = os.path.join(*req_message.payload["path"])
            try:
                app_runner.create_persisted_script(path)
            except Exception as error:
                response.payload = {"error": str(error)}
        elif req_message.type == "deleteSourceFile":
            path = os.path.join(*req_message.payload["path"])
            try:
                app_runner.delete_persisted_script(path)
            except Exception as error:
                response.payload = {"error": str(error)}
        elif req_message.type == "renameSourceFile":
            from_path = os.path.join(*req_message.payload["from"])
            to_path = os.path.join(*req_message.payload["to"])
            try:
                app_runner.rename_persisted_script(from_path, to_path)
            except Exception as error:
                response.payload = {"error": str(error)}
        elif req_message.type == "listResources":
            res = await app_runner.list_resources(session_id, req_message.payload["resource_type"])
            response.payload = res.payload
        elif req_message.type == "uploadSourceFile":
            path = os.path.join(*req_message.payload["path"])

            try:
                content = base64.b64decode(req_message.payload["content"])
                app_runner.create_persisted_script(path, content)
                response.payload = {"sourceFiles": app_runner.source_files}
            except Exception as error:
                response.payload = {"error": str(error)}
        elif req_message.type == "writerVaultUpdate":
            await app_runner.writer_vault_refresh(session_id)

        await _send_json_or_queue(session_id, response.model_dump(), websocket)

    async def _handle_keep_alive_message(
        websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming
    ):
        response = WriterWebsocketOutgoing(
            messageType="keepAliveResponse", trackingId=req_message.trackingId, payload=None
        )
        await _send_json_or_queue(session_id, response.model_dump(), websocket)

    async def _handle_state_enquiry_message(
        websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming
    ):
        response = WriterWebsocketOutgoing(
            messageType=f"{req_message.type}Response",
            trackingId=req_message.trackingId,
            payload=None,
        )
        res_payload: Optional[Dict[str, Any]] = None
        apsr: Optional[AppProcessServerResponse] = None
        apsr = await app_runner.handle_state_enquiry(session_id)
        if apsr is not None and apsr.payload is not None:
            res_payload = typing.cast(StateEnquiryResponsePayload, apsr.payload).model_dump()
        if res_payload is not None:
            response.payload = res_payload
        await _send_json_or_queue(session_id, response.model_dump(), websocket)

    async def _handle_hash_request(
        websocket: WebSocket, session_id: str, req_message: WriterWebsocketIncoming
    ):
        response = WriterWebsocketOutgoing(
            messageType=f"{req_message.type}Response",
            trackingId=req_message.trackingId,
            payload=None,
        )
        apsr: Optional[AppProcessServerResponse] = None
        apsr = await app_runner.handle_hash_request(
            session_id, HashRequestPayload(message=req_message.payload.get("message", ""))
        )
        if apsr is not None and apsr.payload is not None:
            response.payload = typing.cast(HashRequestResponsePayload, apsr.payload).model_dump()
        await _send_json_or_queue(session_id, response.model_dump(), websocket)

    async def _stream_outgoing_announcements(websocket: WebSocket, session_id: str):
        """
        Handles outgoing communications to the client (announcements).
        """

        WEBSOCKET_CODE_UPDATE_CODE = 4001
        session_queue: asyncio.Queue = asyncio.Queue()
        app_runner.announcement_queues[session_id] = session_queue

        try:
            while True:
                announcement_data = await session_queue.get()
                announcement = WriterWebsocketOutgoing(
                    messageType="announcement", trackingId=-1, payload=announcement_data
                )
                if websocket.application_state == WebSocketState.CONNECTED:
                    await websocket.send_json(announcement.dict())
                if announcement_data.get("type") == "codeUpdate":
                    await websocket.close(WEBSOCKET_CODE_UPDATE_CODE, "Code update.")
                    return
        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            raise
        finally:
            if app_runner.announcement_queues.get(session_id) is None:
                return
            del app_runner.announcement_queues[session_id]

    @app.websocket("/api/stream")
    async def stream(websocket: WebSocket):
        """Initialises incoming and outgoing communications on the stream."""

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
        
        try:
            queued_messages = await app_runner.retrieve_messages(session_id)
            for message in queued_messages:
                await websocket.send_json(message)
            await app_runner.clear_messages(session_id)
        except (WebSocketDisconnect, RuntimeError):
            return

        task1 = asyncio.create_task(_stream_incoming_requests(websocket, session_id))
        task2 = asyncio.create_task(_stream_outgoing_announcements(websocket, session_id))

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
        app.mount("/static", StaticFiles(directory=str(user_app_static_path)), name="user_static")

    user_app_extensions_path = pathlib.Path(user_app_path) / "extensions"
    if user_app_extensions_path.exists():
        app.mount(
            "/extensions", StaticFiles(directory=str(user_app_extensions_path)), name="extensions"
        )

    server_path = pathlib.Path(__file__)
    server_static_path = server_path.parent / "static"
    if server_static_path.exists():
        _mount_render_index_html(app, server_static_path)
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

    print(
        f"{run_name} is available at:{END_TOKEN}{GREEN_TOKEN} http://{host}:{port}{END_TOKEN}",
        flush=True,
    )


def register_auth(
    auth: "Auth",
    callback: Optional[Callable[[Request, str, dict], None]] = None,
    unauthorized_action: Optional[Callable[[Request, "Unauthorized"], Response]] = None,
):
    auth.register(app, callback=callback, unauthorized_action=unauthorized_action)


def serve(
    app_path: str,
    mode: ServeMode,
    port: Optional[int],
    host,
    enable_remote_edit=False,
    enable_server_setup=False
):
    """Initialises the web server."""

    print_init_message()

    def on_load():
        run_name = "Builder" if mode == "edit" else "App"
        print_route_message(run_name, port, host)

    """
    Loading of the server_setup.py is active by default 
    when Writer Framework is launched with the run command.
    """
    if port is None:
        mode_allowed_ports = {"run": (3005, 3099), "edit": (4005, 4099)}

        port = _next_localhost_available_port(mode_allowed_ports[mode])

    enable_server_setup = mode == "run" or enable_server_setup
    app = get_asgi_app(
        app_path,
        mode,
        enable_remote_edit,
        on_load=on_load,
        enable_server_setup=enable_server_setup
    )
    log_level = "warning"
    uvicorn.run(
        app, host=host, port=port, log_level=log_level, ws_max_size=MAX_WEBSOCKET_MESSAGE_SIZE
    )


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


def configure_webpage_metadata(
    title: Union[str, Callable[[], str]] = "Writer Framework",
    meta: Optional[Union[Dict[str, Any], Callable[[], Dict[str, Any]]]] = None,
    opengraph_tags: Optional[Union[Dict[str, Any], Callable[[], Dict[str, Any]]]] = None,
):
    """
    Configures the page header for SEO and social networks from `server_setup` module.

    >>> writer.serve.configure_webpage_metadata(
    >>>     title="my App",
    >>>     meta={
    >>>         "description": "my amazing app",
    >>>         "keywords": "WF, Amazing, AI App",
    >>>         "author": "Amazing company"
    >>>     }
    >>>)

    Meta will accept description, keywords, author. Other meta tags as view port won't be supported.

    Settings accept functions to adapt content based on application data.

    >>> def generated_title():
    >>>     return "My App" # load title using info from database

    >>> def generated_meta_tags():
    >>>     {
    >>>         "description": "my amazing app",
    >>>         "keywords": "WF, Amazing, AI App",
    >>>         "author": "Amazing company"
    >>>     }

    >>> writer.serve.configure_webpage_metadata(
    >>>     title=generated_title
    >>>     meta=generated_meta_tags
    >>> )

    OpenGraph tags are used by social networks to display information about the page. WF support them.

    >>> writer.serve.configure_webpage_metadata(
    >>>     title=generated_title
    >>>     opengraph_tags= {
    >>>         "og:title": "My App",
    >>>         "og:description": "My amazing app",
    >>>         "og:image": "https://myapp.com/logo.png",
    >>>         "og:url": "https://myapp.com"
    >>>     }
    >>> )

    >>> def generated_opengraph_tags():
    >>>     return {
    >>>         "og:title": "My App",
    >>>         "og:description": "My amazing app",
    >>>     }

    >>> writer.serve.configure_webpage_metadata(
    >>>     title=generated_title
    >>>     opengraph_tags= generated_opengraph_tags
    >>> )

    ---

    WF replaces the placeholders <!-- {{ meta }} -->, <!-- {{ opengraph_tags }} -->
    and the <title>Writer framework<title> tag in the index.html file.

    :param title: The title of the page. Default: "Writer Framework"
    :param meta: A list of meta tags. Default: {}
    :param opengraph_tags: A dictionary of OpenGraph tags. Default: {}
    """
    app.state.title = title
    app.state.meta = meta if meta is not None else {}
    app.state.opengraph_tags = opengraph_tags if opengraph_tags is not None else {}


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
    for f in wf_root_static_assets():
        if f.is_file():
            app.get(f"/{f.name}")(lambda: FileResponse(f))
        if f.is_dir():
            app.mount(f"/{f.name}", StaticFiles(directory=f), name=f"server_static_{f}")


def _mount_render_index_html(app: FastAPI, server_static_path: pathlib.Path):
    """
    Serves the main page with the title that has been configured.

    :param app:
    :param server_static_path:
    :return:
    """

    def _render_index_html():
        with io.open(server_static_path.joinpath("index.html"), "r", encoding="utf-8") as f:
            index_html = f.read()
            if hasattr(app.state, "title"):
                index_html = index_html.replace(
                    "<title>Writer Framework</title>",
                    f"<title>{html.escape(app.state.title)}</title>",
                )

            if hasattr(app.state, "meta"):
                meta = app.state.meta() if callable(app.state.meta) else app.state.meta
                meta_tags = "\n".join(
                    [f'<meta name="{k}" content="{html.escape(v)}">' for k, v in meta.items()]
                )
                index_html = index_html.replace("<!-- {{ meta }} -->", meta_tags)
            else:
                index_html = index_html.replace("<!-- {{ meta }} -->", "")

            if hasattr(app.state, "opengraph_tags"):
                opengraph_tags = (
                    app.state.opengraph_tags()
                    if callable(app.state.opengraph_tags)
                    else app.state.opengraph_tags
                )
                opengraph_tags = "\n".join(
                    [
                        f'<meta property="{k}" content="{html.escape(v)}">'
                        for k, v in opengraph_tags.items()
                    ]
                )
                index_html = index_html.replace("<!-- {{ opengraph_tags }} -->", opengraph_tags)
            else:
                index_html = index_html.replace("<!-- {{ opengraph_tags }} -->", "")

        return Response(content=index_html, media_type="text/html")

    return app.get("/")(_render_index_html)


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
    for f in server_static_path.glob("*"):
        all_static_assets.append(f)

    return all_static_assets


def _execute_server_setup_hook(user_app_path: str) -> None:
    """
    Runs the server_setup.py module if present in the application directory.

    """
    server_setup_path = os.path.join(user_app_path, "server_setup.py")
    if os.path.isfile(server_setup_path):
        spec = cast(
            ModuleSpec, importlib.util.spec_from_file_location("server_setup", server_setup_path)
        )
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
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()
        if result != 0:
            return port

    raise OSError(
        f"No free port found to start the server between {port_range[0]} and {port_range[1]} ."
    )
