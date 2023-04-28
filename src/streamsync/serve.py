import asyncio
import multiprocessing
import threading
from typing import Any, Dict, List, Optional, Union
import typing
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect
from streamsync.ss_types import (AppProcessServerResponse, ComponentUpdateRequestPayload, EventResponsePayload, InitRequestBody, InitResponseBodyEdit,
                                 InitResponseBodyRun, InitSessionRequestPayload, InitSessionResponsePayload, ServeMode, StreamsyncEvent, StreamsyncWebsocketIncoming, StreamsyncWebsocketOutgoing)
import os
import uvicorn
from streamsync.app_runner import AppRunner
from urllib.parse import urlsplit
import logging
from streamsync import VERSION

MAX_WEBSOCKET_MESSAGE_SIZE = 201*1024*1024


def get_asgi_app(user_app_path: str, serve_mode: ServeMode) -> FastAPI:
    if serve_mode not in ["run", "edit"]:
        raise ValueError("""Invalid mode. Must be either "run" or "edit".""")

    app_runner = AppRunner(user_app_path, serve_mode)
    app_runner.load()
    asgi_app = FastAPI()

    def _check_origin_header(origin_header: Optional[str]) -> bool:
        if serve_mode not in ("edit"):
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
            components=payload.components
        )

    def _get_edit_starter_pack(payload: InitSessionResponsePayload):
        saved_code: Optional[str] = app_runner.saved_code
        run_code: Optional[str] = app_runner.run_code

        return InitResponseBodyEdit(
            mode="edit",
            sessionId=payload.sessionId,
            userState=payload.userState,
            mail=payload.mail,
            components=payload.components,
            userFunctions=payload.userFunctions,
            savedCode=saved_code,
            runCode=run_code
        )

    @asgi_app.post("/api/init")
    async def init(initBody: InitRequestBody, request: Request) -> Union[InitResponseBodyRun, InitResponseBodyEdit]:

        """
        Handles session init and provides a "starter pack" to the frontend.
        """

        origin_header = request.headers.get("origin")
        if not _check_origin_header(origin_header):
            wrong_origin_message = "A session request with origin %s was rejected. For security reasons, only local origins are allowed in edit mode."
            logging.error(wrong_origin_message, origin_header)
            raise HTTPException(
                status_code=403, detail="Incorrect origin. Only local origins are allowed.")

        response = await app_runner.init_session(InitSessionRequestPayload(
            cookies=dict(request.cookies),
            headers=dict(request.headers),
            proposedSessionId=initBody.proposedSessionId
        ))
        status = response.status

        if status == "error" or response.payload is None:
            raise HTTPException(status_code=403, detail="Session rejected.")

        if serve_mode == "run":
            return _get_run_starter_pack(response.payload)

        if serve_mode == "edit":
            return _get_edit_starter_pack(response.payload)

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
                req_message = StreamsyncWebsocketIncoming.parse_obj(
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

        while True:
            req_message_raw = await websocket.receive_json()

            try:
                req_message = StreamsyncWebsocketIncoming.parse_obj(
                    req_message_raw)
            except ValidationError:
                logging.error("Incorrect incoming request.")
                return

            response = StreamsyncWebsocketOutgoing(
                messageType=f"{req_message.type}Response",
                trackingId=req_message.trackingId,
                payload=None
            )

            is_session_ok = await app_runner.check_session(session_id)
            if not is_session_ok:
                return

            apsr: Optional[AppProcessServerResponse] = None
            res_payload: Optional[Dict[str, Any]] = None

            if req_message.type == "event":
                apsr = await app_runner.handle_event(
                    session_id, StreamsyncEvent(
                        type=req_message.payload["type"],
                        instancePath=req_message.payload["instancePath"],
                        payload=req_message.payload["payload"]
                    ))
                if apsr is not None and apsr.payload is not None:
                    res_payload = typing.cast(
                        EventResponsePayload, apsr.payload).dict()
            if serve_mode == "edit":
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

            if res_payload is not None:
                response.payload = res_payload

            try:
                await websocket.send_json(response.dict())
            except WebSocketDisconnect:
                return

    async def _stream_outgoing_announcements(websocket: WebSocket):

        """
        Handles outgoing communications to client (announcements).
        """

        from asyncio import sleep
        code_version = app_runner.get_run_code_version()
        while True:
            await sleep(1)
            current_code_version = app_runner.get_run_code_version()
            if code_version == current_code_version:
                continue
            code_version = current_code_version

            announcement = StreamsyncWebsocketOutgoing(
                messageType="announcement",
                trackingId=-1,
                payload={
                    "announce": "codeUpdate"
                }
            )

            try:
                await websocket.send_json(announcement.dict())
            except (WebSocketDisconnect):
                return

    @asgi_app.websocket("/api/stream")
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
            task1.cancel()
            task2.cancel()
        except asyncio.CancelledError:
            logging.warning("Cancelled")

    @asgi_app.on_event("shutdown")
    async def shutdown_event():
        """ Shuts down the AppRunner when the server is shut down. """

        app_runner.shut_down()

    # Mount static paths

    user_app_static_path = os.path.join(user_app_path, "static")
    asgi_app.mount(
        "/static", StaticFiles(directory=user_app_static_path), name="user_static")

    server_path = os.path.dirname(__file__)
    server_static_path = os.path.join(server_path, "static")
    asgi_app.mount(
        "/", StaticFiles(directory=server_static_path, html=True), name="server_static")

    # Return

    return asgi_app


def print_init_message(run_name: str, port: int, host: str):
    GREEN_TOKEN = "\033[92m"
    END_TOKEN = "\033[0m"

    print(f"""{ GREEN_TOKEN }
     _                                     
 ___| |_ ___ ___ ___ _____ ___ _ _ ___ ___ 
|_ -|  _|  _| -_| .'|     |_ -| | |   |  _|
|___|_| |_| |___|__,|_|_|_|___|_  |_|_|___|  v{VERSION}
                              |___|

 {END_TOKEN}{run_name} is available at:{END_TOKEN}{GREEN_TOKEN} http://{host}:{port}
    
{END_TOKEN}""")


def serve(app_path: str, mode: ServeMode, port, host):
    """ Initialises the web server. """

    asgi_app = get_asgi_app(app_path, mode)

    run_name = "Builder" if mode == "edit" else "App"
    print_init_message(run_name, port, host)

    log_level = "warning"

    uvicorn.run(asgi_app, host=host,
                port=port, log_level=log_level, ws_max_size=MAX_WEBSOCKET_MESSAGE_SIZE)
