import asyncio
import concurrent.futures
import importlib.util
import io
import logging
import logging.handlers
import multiprocessing
import multiprocessing.connection
import multiprocessing.synchronize
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import zipfile
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Union, cast

import watchdog.events
from pydantic import ValidationError
from watchdog.observers.polling import PollingObserver

from writer import VERSION, audit_and_fix, core_ui, crypto, vault, wf_project
from writer.core import (
    Config,
    EventHandlerRegistry,
    MiddlewareRegistry,
    WriterSession,
    use_request_context,
)
from writer.core_ui import ingest_bmc_component_tree
from writer.logs import use_logging_redirect, use_stdout_redirect
from writer.ss_types import (
    AppProcessServerRequest,
    AppProcessServerRequestPacket,
    AppProcessServerResponse,
    AppProcessServerResponsePacket,
    ComponentDefinition,
    ComponentUpdateRequest,
    ComponentUpdateRequestPayload,
    EventRequest,
    EventResponsePayload,
    HashRequest,
    HashRequestPayload,
    HashRequestResponsePayload,
    InitSessionRequest,
    InitSessionRequestPayload,
    InitSessionResponsePayload,
    ListResourcesRequest,
    ListResourcesRequestPayload,
    QueueMessageRequest,
    ServeMode,
    SourceFilesDirectory,
    StateContentRequest,
    StateContentResponsePayload,
    StateEnquiryRequest,
    StateEnquiryResponsePayload,
    WriterApplicationInformation,
    WriterEvent,
    WriterVaultUpdateRequest,
)
from writer.wf_project import WfProjectContext

user_code_logger = logging.getLogger("user_code")


class MessageHandlingException(Exception):
    pass


class SessionPruner(threading.Thread):
    """
    Prunes sessions in intervals, without interfering with the AppProcess server thread.
    """

    PRUNE_SESSIONS_INTERVAL_SECONDS = 60

    def __init__(self, is_session_pruner_terminated: threading.Event):
        super().__init__(name="SessionPrunerThread")
        self.is_session_pruner_terminated = is_session_pruner_terminated

    def run(self) -> None:
        import writer

        while True:
            self.is_session_pruner_terminated.wait(
                timeout=SessionPruner.PRUNE_SESSIONS_INTERVAL_SECONDS
            )
            if self.is_session_pruner_terminated.is_set():
                return
            writer.session_manager.prune_sessions()


class AppProcess(multiprocessing.Process):
    """
    Writer Framework runs the user's app code using an isolated process, based on this class.
    The main process is able to communicate with the user app process via app messages (e.g. event, componentUpdate).
    """

    def __init__(
        self,
        client_conn: multiprocessing.connection.Connection,
        server_conn: multiprocessing.connection.Connection,
        app_path: str,
        mode: ServeMode,
        run_code: str,
        bmc_components: Dict,
        is_app_process_server_ready: multiprocessing.synchronize.Event,
        is_app_process_server_failed: multiprocessing.synchronize.Event,
    ):
        super().__init__(name="AppProcess")
        self.client_conn = client_conn
        self.server_conn = server_conn
        self.app_path = app_path
        self.mode = mode
        self.run_code = run_code
        self.bmc_components = bmc_components
        self.is_app_process_server_ready = is_app_process_server_ready
        self.is_app_process_server_failed = is_app_process_server_failed
        self.logger = logging.getLogger("app")
        self.handler_registry = EventHandlerRegistry()
        self.middleware_registry = MiddlewareRegistry()
        self.executor: Optional[concurrent.futures.ThreadPoolExecutor] = None

    def _load_module(self) -> ModuleType:
        """
        Loads the entry point for the user code in module writeruserapp.
        """

        module_name = "writeruserapp"
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        if spec is None:
            raise ModuleNotFoundError("Couldn't load app module spec.")
        module: ModuleType = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        globals()[module_name] = module

        return module

    def _get_user_functions(self) -> List[EventHandlerRegistry.HandlerMeta]:
        """
        Returns functions exposed in the user code module and registered modules,
        which are potential event handlers, using the handler registry.
        """
        return self.handler_registry.gather_handler_meta()

    def _handle_session_init(
        self, payload: InitSessionRequestPayload
    ) -> InitSessionResponsePayload:
        """
        Handles session initialisation and provides a starter pack.
        """

        import traceback as tb

        import writer

        session = writer.session_manager.get_session(
            payload.proposedSessionId, restore_initial_mail=True
        )
        if session is None:
            session = writer.session_manager.get_new_session(
                payload.cookies, payload.headers, payload.proposedSessionId
            )

        if session is None:
            raise MessageHandlingException("Session rejected.")

        user_state = {}
        try:
            user_state = session.session_state.user_state.to_dict()
        except BaseException:
            session.session_state.add_log_entry("error", "Serialisation error", tb.format_exc())

        ui_component_tree = core_ui.export_component_tree(
            session.session_component_tree, mode=writer.Config.mode
        )

        headers = session.headers or {}
        writer_application: Optional[WriterApplicationInformation] = None
        writer_app_id = headers.get("x-agent-id") or os.getenv("WRITER_APP_ID")
        writer_org_id = headers.get("x-organization-id") or os.getenv("WRITER_ORG_ID")
        writer_base_url = os.getenv("WRITER_BASE_URL", "https://api.writer.com")
        if writer_app_id is not None and writer_org_id is not None:
            writer_application = WriterApplicationInformation(
                id=writer_app_id,
                organizationId=writer_org_id,
                baseUrl=writer_base_url
            )
            if writer.Config.mode == "edit":
                writer_application.apiKey = os.getenv("WRITER_API_KEY")

        res_payload = InitSessionResponsePayload(
            userState=user_state,
            sessionId=session.session_id,
            mail=session.session_state.mail,
            components=ui_component_tree,
            userFunctions=self._get_user_functions(),
            featureFlags=writer.Config.feature_flags,
            writerApplication=writer_application,
        )

        session.session_state.clear_mail()

        return res_payload

    def _handle_event(self, session: WriterSession, event: WriterEvent) -> EventResponsePayload:
        import traceback as tb

        result = session.event_handler.handle(event)

        mutations = {}

        try:
            mutations = session.session_state.user_state.get_mutations_as_dict()
        except BaseException:
            session.session_state.add_log_entry(
                "error",
                "Serialisation Error",
                "An exception was raised during serialisation.",
                tb.format_exc(),
            )

        mail = session.session_state.mail

        ui_component_tree = core_ui.export_component_tree(
            session.session_component_tree, mode=Config.mode, only_update=True
        )

        res_payload = EventResponsePayload(
            result=result, mutations=mutations, components=ui_component_tree, mail=mail
        )
        session.session_state.clear_mail()

        return res_payload

    def _handle_state_enquiry(self, session: WriterSession) -> StateEnquiryResponsePayload:
        import traceback as tb

        mutations = {}

        try:
            mutations = session.session_state.user_state.get_mutations_as_dict()
        except BaseException:
            session.session_state.add_log_entry(
                "error",
                "Serialisation Error",
                "An exception was raised during serialisation.",
                tb.format_exc(),
            )

        mail = session.session_state.mail

        res_payload = StateEnquiryResponsePayload(mutations=mutations, mail=mail)

        session.session_state.clear_mail()

        return res_payload

    def _handle_state_content(self, session: WriterSession) -> StateContentResponsePayload:
        serialized_state = {}
        try:
            serialized_state = session.session_state.user_state.to_raw_state()
        except BaseException:
            import traceback as tb

            session.session_state.add_log_entry(
                "error",
                "Serialisation Error",
                "An exception was raised during serialisation.",
                tb.format_exc(),
            )

        return StateContentResponsePayload(state=serialized_state)

    def _handle_hash_request(self, req_payload: HashRequestPayload) -> HashRequestResponsePayload:
        res_payload = HashRequestResponsePayload(message=crypto.get_hash(req_payload.message))
        return res_payload

    def _handle_component_update(
        self, session: WriterSession, payload: ComponentUpdateRequestPayload
    ) -> None:
        import writer

        ingest_bmc_component_tree(writer.base_component_tree, payload.components)
        ingest_bmc_component_tree(session.session_component_tree, payload.components, True)

    def _handle_list_resources(
        self, session: WriterSession, req: ListResourcesRequestPayload
    ) -> AppProcessServerResponse:
        organization_id = os.environ.get("WRITER_ORG_ID", None)
        if req.resource_type == "graphs":
            from writerai import APIConnectionError

            from writer.ai import list_graphs

            try:
                graphs = list_graphs()
                raw_graphs = [
                    {
                        "name": graph.name,
                        "id": graph.id,
                        "description": graph.description,
                        "organization_id": organization_id,
                    }
                    for graph in graphs
                ]
                return AppProcessServerResponse(
                    status="ok", status_message=None, payload={"data": raw_graphs}
                )
            except (RuntimeError, APIConnectionError) as e:
                return AppProcessServerResponse(status="error", status_message=str(e), payload=None)

        if req.resource_type == "applications":
            from writerai import APIConnectionError

            from writer.ai import apps

            try:
                applications = apps.list()
                raw_apps = [
                    {
                        "name": app.name,
                        "id": app.id,
                        "type": app.type,
                        "status": app.status,
                        "organization_id": organization_id,
                        "inputs": {i.name: "" for i in app.inputs},
                    }
                    for app in applications
                ]
                return AppProcessServerResponse(
                    status="ok", status_message=None, payload={"data": raw_apps}
                )
            except (RuntimeError, APIConnectionError) as e:
                return AppProcessServerResponse(status="error", status_message=str(e), payload=None)

        if req.resource_type == "models":
            from writerai import APIConnectionError

            from writer.ai import WriterAIManager

            try:
                client = WriterAIManager.acquire_client()
                models_response = client.models.list()
                models = models_response.models
                raw_models = [
                    {
                        "name": model.name,
                        "id": model.id
                    }
                    for model in models
                ]
                return AppProcessServerResponse(
                    status="ok", status_message=None, payload={"data": raw_models}
                )
            except (RuntimeError, APIConnectionError) as e:
                return AppProcessServerResponse(status="error", status_message=str(e), payload=None)

        return AppProcessServerResponse(
            status="error",
            status_message=f"could not load unknow resources {req.resource_type}",
            payload=None,
        )

    def _handle_message(
        self, session_id: str, request: AppProcessServerRequest
    ) -> AppProcessServerResponse:
        """
        Handles messages from the main process to the app's isolated process.
        """
        import writer

        with use_request_context(session_id, request):
            session = None
            type = request.type

            if type == "sessionInit":
                si_req_payload = InitSessionRequestPayload.model_validate(request.payload)
                return AppProcessServerResponse(
                    status="ok",
                    status_message=None,
                    payload=self._handle_session_init(si_req_payload),
                )

            session = writer.session_manager.get_session(session_id)
            if not session:
                raise MessageHandlingException("Session not found.")
            session.update_last_active_timestamp()

            if type == "checkSession":
                return AppProcessServerResponse(status="ok", status_message=None, payload=None)

            if type == "event":
                ev_req_payload = WriterEvent.model_validate(request.payload)
                return AppProcessServerResponse(
                    status="ok",
                    status_message=None,
                    payload=self._handle_event(session, ev_req_payload),
                )

            if type == "stateEnquiry":
                return AppProcessServerResponse(
                    status="ok", status_message=None, payload=self._handle_state_enquiry(session)
                )

            if type == "stateContent":
                return AppProcessServerResponse(
                    status="ok", status_message=None, payload=self._handle_state_content(session)
                )

            if type == "setUserinfo":
                session.userinfo = request.payload
                return AppProcessServerResponse(status="ok", status_message=None, payload=None)

            if type == "queueMessage":
                session.queued_messages.append(request.payload)
                return AppProcessServerResponse(status="ok", status_message=None, payload=None)

            if type == "retrieveMessages":
                return AppProcessServerResponse(status="ok", status_message=None, payload=session.queued_messages)

            if type == "clearMessages":
                session.queued_messages = []
                return AppProcessServerResponse(status="ok", status_message=None, payload=None)

            if self.mode == "edit" and type == "hashRequest":
                hash_request_payload = HashRequestPayload.model_validate(request.payload)
                return AppProcessServerResponse(
                    status="ok",
                    status_message=None,
                    payload=self._handle_hash_request(hash_request_payload),
                )

            if self.mode == "edit" and type == "componentUpdate":
                cu_req_payload = ComponentUpdateRequestPayload.model_validate(request.payload)
                self._handle_component_update(session, cu_req_payload)
                return AppProcessServerResponse(status="ok", status_message=None, payload=None)

            if self.mode == "edit" and type == "listResources":
                list_req_payload = ListResourcesRequestPayload.model_validate(request.payload)
                return self._handle_list_resources(session, list_req_payload)

            if self.mode == "edit" and type == "writerVaultUpdate":
                vault.writer_vault.refresh()
                return AppProcessServerResponse(
                    status="ok",
                    status_message=None,
                    payload=None,
                )

            raise MessageHandlingException("Invalid event.")

    def _execute_user_code(self) -> None:
        """
        Executes the user code and captures standard output.
        """

        import io

        import writer

        writeruserapp = sys.modules.get("writeruserapp")
        if writeruserapp is None:
            raise ValueError("Couldn't find app module (writeruserapp).")

        code_path = os.path.join(self.app_path, "main.py")
        with (
            use_stdout_redirect(lambda entry: writer.core.initial_state.add_log_entry("info", "Stdout message during initialization", entry)),
            use_logging_redirect(lambda entry: writer.core.initial_state.add_log_entry("info", "Logs during initialization", entry)),
        ):
            writeruserapp.__dict__["logger"] = user_code_logger
            code = compile(self.run_code, code_path, "exec")
            exec(code, writeruserapp.__dict__)

        # Register non-private functions as handlers
        self.handler_registry.register_module(writeruserapp)

    def _apply_configuration(self) -> None:
        import writer

        writer.Config.mode = self.mode
        writer.Config.logger = self.logger

        if self.mode == "edit":
            writer.Config.is_mail_enabled_for_log = True
        elif self.mode == "run":
            writer.Config.is_mail_enabled_for_log = False

    def _terminate_early(self) -> None:
        self.is_app_process_server_failed.set()
        self.is_app_process_server_ready.set()
        with self.server_conn_lock:
            self.server_conn.send(None)

    def _main(self) -> None:
        self._apply_configuration()
        import os

        os.chdir(self.app_path)
        self._load_module()
        # Allows for relative imports from the app's path
        sys.path.append(self.app_path)

        import traceback as tb

        import writer

        terminate_early = False

        try:
            ingest_bmc_component_tree(writer.base_component_tree, self.bmc_components)
        except BaseException:
            writer.core.initial_state.add_log_entry(
                "error",
                "UI Components Error",
                "Couldn't load components. An exception was raised.",
                tb.format_exc(),
            )
            if self.mode == "run":
                terminate_early = True

        try:
            self._execute_user_code()
        except BaseException:
            # Initialisation errors will be sent to all sessions via mail during session initialisation

            writer.core.initial_state.add_log_entry(
                "error",
                "Code Error",
                "Couldn't execute code. An exception was raised.",
                tb.format_exc(),
            )

            # Exit if in run mode

            if self.mode == "run":
                terminate_early = True

        if terminate_early:
            self._terminate_early()
            return

        self._run_app_process_server()

    def _handle_message_and_get_packet(
        self, message_id: int, session_id: str, request: AppProcessServerRequest
    ) -> AppProcessServerResponsePacket:
        response = None
        try:
            response = self._handle_message(session_id, request)
        except (MessageHandlingException, ValidationError) as e:
            response = AppProcessServerResponse(
                status="error", status_message=repr(e), payload=None
            )

        packet: AppProcessServerResponsePacket = (message_id, session_id, response)
        return packet

    def _send_packet(self, packet_future: concurrent.futures.Future) -> None:
        result = packet_future.result()

        with self.server_conn_lock:
            self.server_conn.send(result)

    def _run_app_process_server(self) -> None:
        is_app_process_server_terminated = threading.Event()
        session_pruner = SessionPruner(is_app_process_server_terminated)
        session_pruner.start()

        def terminate_server():
            if is_app_process_server_terminated.is_set():
                return
            self.executor.shutdown(wait=False)
            with self.server_conn_lock:
                self.server_conn.send(None)
                is_app_process_server_terminated.set()
                session_pruner.join()

        def signal_handler(sig, frame):
            terminate_server()

        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except ValueError:
            # No need to handle signal as not main thread
            pass

        self.is_app_process_server_ready.set()
        while True and not is_app_process_server_terminated.is_set():  # Starts app message server
            try:
                if not self.server_conn.poll(1):
                    continue
                packet = self.server_conn.recv()
                if packet is None:  # An empty packet terminates the process
                    # Send empty packet to client for it to close
                    terminate_server()
                    return
                self._handle_app_process_server_packet(packet)
            except Exception as e:
                self.logger.error(f"Unexpected exception in AppProcess server.\n{repr(e)}")
                terminate_server()
                return

    def _handle_app_process_server_packet(self, packet: AppProcessServerRequestPacket) -> None:
        if not self.executor:
            return
        (message_id, session_id, request) = packet
        thread_pool_future = self.executor.submit(
            self._handle_message_and_get_packet, message_id, session_id, request
        )
        thread_pool_future.add_done_callback(self._send_packet)

    def run(self) -> None:
        max_workers = int(os.getenv("WRITER_MAX_WORKERS", (os.cpu_count() or 4) * 10))
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
        )
        self.server_conn_lock = threading.Lock()
        self.client_conn.close()
        self._main()


class FileEventHandler(watchdog.events.PatternMatchingEventHandler):
    """
    Watches for changes in files and triggers code reloads.
    """

    def __init__(self, update_callback: Callable, patterns: List[str]):
        self.update_callback = update_callback
        super().__init__(
            patterns=patterns,
            ignore_patterns=[".*"],
            ignore_directories=False,
            case_sensitive=False,
        )

    def on_any_event(self, event) -> None:
        if event.event_type not in ("modified", "deleted", "created"):
            return
        self.update_callback()


class ThreadSafeAsyncEvent(asyncio.Event):
    """Asyncio event adapted to be thread-safe."""

    def __init__(self):
        super().__init__()
        if self._loop is None:
            self._loop = asyncio.get_event_loop()

    def set(self) -> None:
        self._loop.call_soon_threadsafe(super().set)


class AppProcessListener(threading.Thread):
    """
    Listens to messages from the AppProcess server.
    Notifies receipt via events in response_events and makes the responses available in response_packets.
    """

    def __init__(
        self,
        client_conn: multiprocessing.connection.Connection,
        is_app_process_server_ready: multiprocessing.synchronize.Event,
        response_packets: Dict,
        response_events: Dict,
    ):
        super().__init__(name="AppProcessListenerThread")
        self.client_conn = client_conn
        self.is_app_process_server_ready = is_app_process_server_ready
        self.response_packets = response_packets
        self.response_events = response_events
        self.logger = logging.getLogger("writer")

    def run(self) -> None:
        self.is_app_process_server_ready.wait()
        while True:
            if not self.client_conn.poll(1):
                continue
            try:
                packet = self.client_conn.recv()
            except OSError:
                self.logger.error("Connection to AppProcess closed.")
                return
            if packet is None:
                return
            message_id = packet[0]
            self.response_packets[message_id] = packet
            response_event = self.response_events.get(message_id)
            if response_event:
                response_event.set()
            else:
                raise ValueError(f"No response event found for message {message_id}.")


class LogListener(threading.Thread):
    """
    Logs messages stored in the multiprocessing queue.
    This allows log messages from the AppProcess to be safely managed.
    """

    def __init__(self, log_queue: multiprocessing.Queue):
        super().__init__(name="LogListenerThread")
        self.log_queue = log_queue
        self.logger = logging.getLogger("from_app")

    def run(self) -> None:
        while True:
            message = self.log_queue.get()
            if message is None:
                break
            self.logger.handle(message)


class AppRunner:
    """
    Starts a given user app in a separate process.
    Manages changes to the app.
    Allows for communication with the app via messages.
    """

    UPDATE_CHECK_INTERVAL_SECONDS = 0.2
    WF_PROJECT_SAVE_INTERVAL = float(os.getenv("WRITER_SAVE_INTERVAL", "0.2"))
    MAX_WAIT_NOTIFY_SECONDS = 30

    def __init__(self, app_path: str, mode: str):
        self.server_conn: Optional[multiprocessing.connection.Connection] = None
        self.client_conn: Optional[multiprocessing.connection.Connection] = None
        self.app_process: Optional[AppProcess] = None
        self.run_code: Optional[str] = None
        self.source_files: SourceFilesDirectory = {"children": {}, "type": "directory"}
        self.bmc_components: Optional[Dict] = None
        self.is_app_process_server_ready = multiprocessing.Event()
        self.is_app_process_server_failed = multiprocessing.Event()
        self.app_process_listener: Optional[AppProcessListener] = None
        self.observer: Optional[PollingObserver] = None
        self.app_path: str = app_path
        self.response_events: Dict[int, ThreadSafeAsyncEvent] = {}
        self.response_packets: Dict[int, AppProcessServerResponsePacket] = {}
        self.message_counter = 0
        self.log_queue: multiprocessing.Queue = multiprocessing.Queue()
        self.log_listener: Optional[LogListener] = None
        self.serve_loop: Optional[asyncio.AbstractEventLoop] = None
        self.announcement_queues: Dict[str, asyncio.Queue] = {}
        self.wf_project_context = WfProjectContext(app_path=app_path)

        if mode not in ("edit", "run"):
            raise ValueError("Invalid mode.")

        self.mode = cast(ServeMode, mode)
        self._set_logger()

    def hook_to_running_event_loop(self):
        """
        Sets the properties required to notify the web server of the announcements.
        Should be performed from the event loop which will consume the notifications.
        """

        self.serve_loop = asyncio.get_running_loop()

    def _set_logger(self):
        logger = logging.getLogger("app_runner")
        logger.addHandler(logging.handlers.QueueHandler(self.log_queue))
        self.log_listener = LogListener(self.log_queue)
        self.log_listener.start()

    def _start_fs_observer(self):
        # If observer exists but isn't alive, we need to recreate it
        # (can't restart a stopped PollingObserver)
        if self.observer is not None and not self.observer.is_alive():
            logging.info("[Observer Debug] Stopping dead observer before recreating")
            try:
                self.observer.stop()
                self.observer.join(timeout=2.0)
            except Exception as e:
                logging.warning("[Observer Debug] Error stopping dead observer: %s", e)
            self.observer = None
        
        if self.observer is None:
            logging.info("[Observer Debug] Creating new PollingObserver")
            self.observer = PollingObserver(AppRunner.UPDATE_CHECK_INTERVAL_SECONDS)
        
        logging.info("[Observer Debug] Scheduling file event handler for path: %s", self.app_path)
        self.observer.schedule(
            FileEventHandler(self.reload_code_from_saved, patterns=["*.py"]),
            path=self.app_path,
            recursive=True,
        )
        # See _install_requirements docstring for info
        # self.observer.schedule(
        #     FileEventHandler(self._install_requirements, patterns=["requirements.txt"]),
        #     path=self.app_path,
        # )
        if not self.observer.is_alive():
            logging.info("[Observer Debug] Starting observer")
            self.observer.start()
            logging.info("[Observer Debug] Observer started successfully")
        else:
            logging.info("[Observer Debug] Observer already alive, not restarting")

    def _start_wf_project_process_write_files(self):
        wf_project.start_process_write_files_async(
            self.wf_project_context, AppRunner.WF_PROJECT_SAVE_INTERVAL
        )

    def _install_requirements(self) -> None:
        """
        Not used anywhere anymore as this method of installing dependencies is not supported.
        Left because might change in the future.
        """

        logger = logging.getLogger("writer")
        logger.debug("\nDetected changes in requirements.txt. Installing dependencies...")
        try:
            # Run pip install command
            subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                check=True,
                capture_output=True,
                text=True,
                # stdout=subprocess.DEVNULL,  # Suppress pip output
                cwd=self.app_path,
            )
            logger.debug("Dependencies installed successfully, restart server!\n")
            self.reload_code_from_saved()
        except subprocess.CalledProcessError as e:
            logger.warning(f"Error installing dependencies: {e.stderr}")
            self.queue_announcement(
                "mail",
                [
                    {
                        "type": "logEntry",
                        "payload": {
                            "type": "error",
                            "title": "Error installing dependencies",
                            "message": "The dependencies specified on `requirements.txt` could not be installed.",
                            "code": e.stderr,
                        },
                    }
                ],
            )
        except Exception as e:
            logger.warning(f"Unexpected error: {e}")

    def load(self) -> None:
        self.run_code = self.load_persisted_script("main.py")
        self.source_files = wf_project.build_source_files(self.app_path)
        self.bmc_components = self._load_persisted_components()

        if self.mode == "edit":
            self._start_wf_project_process_write_files()
            self._start_fs_observer()

        self._start_app_process()

        # We have to create new processes as wf_projet_process before subscribing to signal.
        # When a new process is create, the parent process is fork. The child would also subscribe to signal.
        #
        # When signal happen, both process will answer and one of them raise error due to mismatch between
        # parent pid and pid.
        self._subscribe_terminal_signal()

    async def dispatch_message(
        self, session_id: str, request: AppProcessServerRequest
    ) -> AppProcessServerResponse:
        """
        Sends a message to the AppProcess server, waits for the listener to obtain a response and returns it.
        """

        message_id = self.message_counter
        self.message_counter += 1
        is_response_ready = ThreadSafeAsyncEvent()
        self.response_events[message_id] = is_response_ready
        packet: AppProcessServerRequestPacket = (message_id, session_id, request)

        if self.client_conn is None:
            raise ValueError("Cannot dispatch message. No connection to AppProcess server is set.")
        self.client_conn.send(packet)

        await is_response_ready.wait()  # Set by the listener thread

        response_packet = self.response_packets.get(message_id)
        if response_packet is None:
            raise ValueError(f"Empty packet received in response to message {message_id}.")
        response_message_id, response_session_id, response = response_packet
        del self.response_packets[message_id]
        del self.response_events[message_id]
        if session_id != response_session_id:
            raise PermissionError("Session mismatch.")
        if message_id != response_message_id:
            raise PermissionError("Message mismatch.")

        return response

    def create_persisted_script(self, file="main.py", content: Union[str, bytes] = ""):
        path = os.path.join(self.app_path, file)
        self._check_file_in_app_path(path)

        if isinstance(content, str):
            mode = "w"
            encoding = "utf-8"
        elif isinstance(content, bytes):
            mode = "wb"
            encoding = None

        with open(path, mode, encoding=encoding) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        self.source_files = wf_project.build_source_files(self.app_path)

    def rename_persisted_script(self, from_path: str, to_path: str):
        if from_path == "main.py":
            raise PermissionError("cannot rename main script")
        if to_path == "main.py":
            raise PermissionError("cannot overwrite main script")

        from_path_abs = os.path.join(self.app_path, from_path)
        self._check_file_in_app_path(from_path_abs)

        to_path_abs = os.path.join(self.app_path, to_path)
        self._check_file_in_app_path(to_path_abs)

        os.makedirs(os.path.dirname(to_path_abs), exist_ok=True)

        try:
            os.rename(from_path_abs, to_path_abs)
        except OSError:
            # If the error is due to the function not being implemented (like S3/Fuse), we fallback to copy/delete
            shutil.copyfile(from_path_abs, to_path_abs)
            os.remove(from_path_abs)

        self.source_files = wf_project.build_source_files(self.app_path)

    def delete_persisted_script(self, file: str):
        if file == "main.py":
            raise PermissionError("cannot delete main script")

        path = os.path.join(self.app_path, file)
        self._check_file_in_app_path(path)

        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

        self.source_files = wf_project.build_source_files(self.app_path)

    def load_persisted_script(self, file="main.py") -> str:
        path = os.path.join(self.app_path, file)
        self._check_file_in_app_path(path)

        logger = logging.getLogger("writer")
        try:
            contents = None
            with open(path, "r", encoding="utf-8") as f:
                contents = f.read()
            return contents
        except FileNotFoundError as error:
            error_msg = f"Couldn't find {file} in the path provided: {self.app_path}"
            logger.error(error_msg)
            if file == "main.py":
                # Don't use sys.exit() - raise exception so it can be caught and handled
                if self.mode == "run":
                    sys.exit(1)
                else:
                    raise ValueError(error_msg) from error
            else:
                raise error

    def _check_file_in_app_path(self, path):
        app_path = os.path.abspath(self.app_path)
        file_path = os.path.abspath(path)
        if file_path == app_path or not file_path.startswith(app_path):
            raise PermissionError(f"{path} should be inside of application ({self.app_path})")
        wf_path = os.path.abspath(os.path.join(self.app_path, ".wf"))
        if file_path.startswith(wf_path):
            raise PermissionError(f"{path} should not be inside of Writer Framework files ({wf_path})")

    def _load_persisted_components(self) -> Dict[str, ComponentDefinition]:
        logger = logging.getLogger("writer")

        if not os.path.isfile(
            os.path.join(self.app_path, ".wf", "components-blueprints_root.jsonl")
        ):
            wf_project.create_default_blueprints_root(self.app_path)

        if not os.path.isdir(os.path.join(self.app_path, ".wf")):
            error_msg = f"Couldn't find .wf directory in the path provided: {self.app_path}"
            logger.error(error_msg)
            # Don't use sys.exit() - raise exception so it can be caught and handled
            if self.mode == "run":
                sys.exit(1)
            else:
                raise ValueError(error_msg)

        _, components = wf_project.read_files(self.app_path)
        components = audit_and_fix.fix_components(components)
        return components

    async def queue_message(self, session_id: str, data: Any) -> AppProcessServerResponse:
        return await self.dispatch_message(session_id, QueueMessageRequest(type="queueMessage", payload=data))

    async def retrieve_messages(self, session_id: str) -> list:
        response = await self.dispatch_message(
            session_id, AppProcessServerRequest(type="retrieveMessages", payload=None)
        )
        if isinstance(response.payload, list):
            return response.payload
        return []

    async def clear_messages(self, session_id: str) -> AppProcessServerResponse:
        response = await self.dispatch_message(
            session_id, AppProcessServerRequest(type="clearMessages", payload=None)
        )
        return response

    async def check_session(self, session_id: str) -> bool:
        response = await self.dispatch_message(
            session_id, AppProcessServerRequest(type="checkSession", payload=None)
        )
        is_ok: bool = response.status == "ok"
        return is_ok

    async def init_session(self, payload: InitSessionRequestPayload) -> AppProcessServerResponse:
        return await self.dispatch_message(
            "anonymous", InitSessionRequest(type="sessionInit", payload=payload)
        )

    async def update_components(
        self, session_id: str, payload: ComponentUpdateRequestPayload
    ) -> AppProcessServerResponse:
        if self.mode != "edit":
            raise PermissionError("Cannot update components in non-update mode.")
        self.bmc_components = payload.components

        wf_project.write_files_async(
            self.wf_project_context,
            metadata={"writer_version": VERSION},
            components=payload.components,
        )

        return await self.dispatch_message(
            session_id, ComponentUpdateRequest(type="componentUpdate", payload=payload)
        )

    async def list_resources(self, session_id: str, resource_type: str) -> AppProcessServerResponse:
        if self.mode != "edit":
            raise PermissionError("Cannot update components in non-update mode.")
        message_payload = ListResourcesRequestPayload(resource_type=resource_type)
        message = ListResourcesRequest(type="listResources", payload=message_payload)
        return await self.dispatch_message(session_id, message)

    async def writer_vault_refresh(self, session_id: str) -> AppProcessServerResponse:
        message = WriterVaultUpdateRequest(type="writerVaultUpdate")
        return await self.dispatch_message(session_id, message)

    async def handle_event(self, session_id: str, event: WriterEvent) -> AppProcessServerResponse:
        return await self.dispatch_message(session_id, EventRequest(type="event", payload=event))

    async def handle_hash_request(
        self, session_id: str, payload: HashRequestPayload
    ) -> AppProcessServerResponse:
        return await self.dispatch_message(
            session_id, HashRequest(type="hashRequest", payload=payload)
        )

    async def handle_state_enquiry(self, session_id: str) -> AppProcessServerResponse:
        return await self.dispatch_message(session_id, StateEnquiryRequest(type="stateEnquiry"))

    async def handle_state_content(self, session_id: str) -> AppProcessServerResponse:
        """
        This method returns the complete status of the application.

        It is only accessible through tests
        """
        return await self.dispatch_message(session_id, StateContentRequest(type="stateContent"))

    def save_code(self, session_id: str, code: str, path: List[str] = ["main.py"]) -> None:
        if self.mode != "edit":
            raise PermissionError("Cannot save code in non-edit mode.")

        filepath = os.path.join(self.app_path, *path)

        # ensure we don't load a file outside of the application (like `../../../etc/passwd`)
        if not os.path.abspath(filepath).startswith(self.app_path):
            raise FileNotFoundError(f"{filepath} is outside of application ({self.app_path})")

        with open(filepath, "w") as f:
            f.write(code)
            f.flush()
            os.fsync(f.fileno())

        self.source_files = wf_project.build_source_files(self.app_path)

    def export_zip(self):
        if self.mode != "edit":
            raise PermissionError("Cannot export in non-edit mode.")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.app_path):
                for file in files:
                    if file.endswith('.pyc'):
                        continue
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, start=self.app_path)
                    zipf.write(full_path, arcname=arcname)
        zip_buffer.seek(0)
        return zip_buffer

    def _sync_folders(self, src: str, dst: str):
        """
        Synchronizes the contents of the source folder to the destination folder in a one-way manner.

        - Copies all files and subdirectories from `src` to `dst`.
        - Creates any missing directories in `dst` to match `src`.
        - Removes any files or directories in `dst` that do not exist in `src`.
        """
        # Create dst if it doesn't exist
        os.makedirs(dst, exist_ok=True)

        # Copy files and folders from src to dst
        for root, dirs, files in os.walk(src):
            rel_path = os.path.relpath(root, src)
            dst_path = os.path.join(dst, rel_path)

            # Create directories in dst
            os.makedirs(dst_path, exist_ok=True)

            # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_path, file)
                shutil.copy2(src_file, dst_file)

        # Remove files and folders in dst that don't exist in src
        for root, dirs, files in os.walk(dst):
            rel_path = os.path.relpath(root, dst)
            src_path = os.path.join(src, rel_path)

            # Remove files not in src
            for file in files:
                dst_file = os.path.join(root, file)
                src_file = os.path.join(src_path, file)
                if not os.path.exists(src_file):
                    os.remove(dst_file)

            # Remove empty directories not in src
            for dir in dirs:
                dst_dir = os.path.join(root, dir)
                src_dir = os.path.join(src_path, dir)
                if not os.path.exists(src_dir):
                    shutil.rmtree(dst_dir)

    async def import_zip(self, zip_path: str):
        logging.info("[Import Debug] Starting import_zip, mode=%s", self.mode)
        
        if self.mode != "edit":
            logging.error("[Import Debug] Import rejected - not in edit mode")
            raise PermissionError("Cannot import in non-edit mode.")

        try:
            logging.info("[Import Debug] Creating temporary directory for extraction")
            with tempfile.TemporaryDirectory() as tmpdir:
                extracted_path = os.path.join(tmpdir, "imported_agent")
                os.makedirs(extracted_path, exist_ok=True)
                
                logging.info("[Import Debug] Extracting zip file: %s", zip_path)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extracted_path)

                logging.info("[Import Debug] Searching for main.py in extracted files")
                main_py_dir = None
                for root, _, files in os.walk(extracted_path):
                    if "main.py" in files:
                        main_py_dir = root
                        logging.info("[Import Debug] Found main.py at: %s", root)
                        break

                if main_py_dir is None:
                    logging.error("[Import Debug] main.py not found in archive")
                    raise ValueError("main.py not found in the imported archive.")

                wf_dir_path = os.path.join(main_py_dir, ".wf")
                if not os.path.isdir(wf_dir_path):
                    logging.error("[Import Debug] .wf directory not found at: %s", wf_dir_path)
                    raise ValueError(".wf directory not found alongside main.py in the archive.")

                # Passed all checks; replace current app contents
                logging.info("[Import Debug] Validation passed, copying app from %s to %s", main_py_dir, self.app_path)
                
                if self.observer is not None:
                    logging.info("[Import Debug] Unscheduling file system observer")
                    try:
                        self.observer.unschedule_all()
                        logging.info("[Import Debug] File system observer unscheduled successfully")
                    except Exception as e:
                        logging.error("[Import Debug] Error unscheduling observer: %s", e, exc_info=True)

                self._sync_folders(main_py_dir, self.app_path)
                logging.info("[Import Debug] Folder sync complete")
                logging.info("[Import Debug] Observer state before restart: %s, alive=%s", 
                            self.observer, 
                            self.observer.is_alive() if self.observer else "N/A")
                
                try:
                    logging.info("[Import Debug] Starting file system observer (may fail on second import)")
                    self._start_fs_observer()
                    logging.info("[Import Debug] File system observer restarted successfully, alive=%s",
                                self.observer.is_alive() if self.observer else "N/A")
                except Exception as e:
                    logging.error("[Import Debug] CRITICAL: Failed to start file system observer: %s", e, exc_info=True)
                    # Don't raise - continue with import even if observer fails
                    logging.warning("[Import Debug] Continuing import without file system observer")
                
                logging.info("[Import Debug] Loading persisted components")
                try:
                    self.bmc_components = self._load_persisted_components()
                    logging.info("[Import Debug] Loaded %d components", len(self.bmc_components) if self.bmc_components else 0)
                except Exception as e:
                    logging.error("[Import Debug] Failed to load persisted components: %s", e, exc_info=True)
                    raise
                
                # Run reload in executor to avoid blocking the event loop
                # Use a short timeout to detect failures quickly
                logging.info("[Import Debug] Starting async reload process")
                try:
                    loop = asyncio.get_event_loop()
                    logging.info("[Import Debug] Got event loop, creating executor")
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        logging.info("[Import Debug] Executor created, submitting reload task")
                        try:
                            success = await asyncio.wait_for(
                                loop.run_in_executor(
                                    executor, 
                                    lambda: self.reload_code_from_saved_nonblocking(wait_timeout=5.0)
                                ),
                                timeout=8.0  # Outer timeout slightly longer than inner
                            )
                            if not success:
                                logging.warning("[Import Debug] App process failed to start after import. Check main.py for errors.")
                            else:
                                logging.info("[Import Debug] App process started successfully")
                        except asyncio.TimeoutError:
                            logging.warning("[Import Debug] App process restart timed out after import, continuing in background")
                        except Exception as e:
                            logging.error("[Import Debug] Exception during reload task execution: %s", e, exc_info=True)
                            raise
                except Exception as e:
                    logging.error("[Import Debug] Exception in async reload process setup: %s", e, exc_info=True)
                    raise
                
                logging.info("[Import Debug] Import completed successfully")
        except zipfile.BadZipFile as e:
            logging.error("[Import Debug] BadZipFile error: %s", e)
            raise ValueError("Uploaded file is not a valid ZIP.")
        except Exception as e:
            logging.error("[Import Debug] Unexpected exception in import_zip: %s", e, exc_info=True)
            raise

    def _clean_process(self) -> None:
        # Terminate the AppProcess server by sending an empty message
        # The empty message will bounce an empty message and terminate the client too
        if self.client_conn is not None:
            self.client_conn.send(None)
        self.is_app_process_server_ready.clear()
        self.is_app_process_server_failed.clear()
        if self.app_process is not None:
            self.app_process.join()
            self.app_process.close()
        if self.app_process_listener is not None:
            self.app_process_listener.join()
        if self.client_conn is not None:
            self.client_conn.close()
        if self.server_conn is not None:
            self.server_conn.close()
        self.response_events = {}
        self.response_packets = {}
        self.app_process = None
        self.app_process_listener = None
        self.client_conn = None
        self.server_conn = None

    def shut_down(self) -> None:
        if self.observer is not None:
            self.observer.unschedule_all()
            self.observer.stop()
            self.observer.join()
        self.log_queue.put(None)
        if self.log_listener is not None:
            self.log_listener.join()

        wf_project.shutdown_process_write_files_async(self.wf_project_context)

        self._clean_process()

    def _start_app_process(self) -> None:
        """Starts app process and waits (blocking) for it to be ready."""
        self._start_app_process_nonblocking()
        self.is_app_process_server_ready.wait()
        if self.mode == "run" and self.is_app_process_server_failed.is_set():
            self.shut_down()
            sys.exit(1)
    
    def _start_app_process_nonblocking(self) -> None:
        """Starts app process without waiting for it to be ready."""
        if self.run_code is None:
            raise ValueError("Cannot start app process. Code hasn't been set.")
        if self.bmc_components is None:
            raise ValueError("Cannot start app process. Components haven't been set.")
        self.is_app_process_server_ready.clear()
        client_conn, server_conn = multiprocessing.Pipe(duplex=True)
        self.client_conn = cast(
            multiprocessing.connection.Connection, client_conn
        )  # for mypy type checking on windows
        self.server_conn = cast(
            multiprocessing.connection.Connection, server_conn
        )  # for mypy type checking on windows

        self.app_process = AppProcess(
            client_conn=self.client_conn,
            server_conn=self.server_conn,
            app_path=self.app_path,
            mode=self.mode,
            run_code=self.run_code,
            bmc_components=self.bmc_components,
            is_app_process_server_ready=self.is_app_process_server_ready,
            is_app_process_server_failed=self.is_app_process_server_failed,
        )
        self.app_process.start()
        self.app_process_listener = AppProcessListener(
            self.client_conn,
            self.is_app_process_server_ready,
            self.response_packets,
            self.response_events,
        )
        self.app_process_listener.start()

    def reload_code_from_saved(self) -> None:
        if not self.is_app_process_server_ready.is_set():
            return
        self.update_code(None, self.load_persisted_script())

    def reload_code_from_saved_nonblocking(self, wait_timeout: Optional[float] = None) -> bool:
        """
        Reloads code from saved files without blocking indefinitely.
        Used during import to restart the app without hanging on errors.
        
        Args:
            wait_timeout: Maximum seconds to wait for app to be ready. None = don't wait.
        
        Returns:
            True if app started successfully, False otherwise.
        """
        logging.info(f"[Import Debug] Starting non-blocking reload, wait_timeout={wait_timeout}")
        
        try:
            logging.info("[Import Debug] Loading persisted script")
            run_code = self.load_persisted_script()
            
            if self.mode != "edit":
                logging.error("[Import Debug] Cannot reload - not in edit mode")
                raise PermissionError("Cannot update code in non-edit mode.")
            
            logging.info("[Import Debug] Building source files")
            self.run_code = run_code
            self.source_files = wf_project.build_source_files(self.app_path)
            
            logging.info("[Import Debug] Cleaning existing process")
            self._clean_process()
            
            logging.info("[Import Debug] Starting new app process (non-blocking)")
            self._start_app_process_nonblocking()
            logging.info("[Import Debug] App process started, not waiting for ready signal yet")
            
            if wait_timeout is not None:
                # Poll with timeout instead of blocking indefinitely
                logging.info(f"[Import Debug] Waiting up to {wait_timeout}s for app to be ready")
                elapsed = 0.0
                poll_interval = 0.1
                while elapsed < wait_timeout:
                    if self.is_app_process_server_ready.is_set():
                        logging.info("[Import Debug] App process is ready!")
                        self.queue_announcement("codeUpdate", None)
                        return True
                    if self.is_app_process_server_failed.is_set():
                        logging.warning("[Import Debug] App process failed to start")
                        return False
                    threading.Event().wait(poll_interval)
                    elapsed += poll_interval
                logging.warning(f"[Import Debug] Timeout after {wait_timeout}s waiting for app to be ready")
                return False
            else:
                # Don't wait at all, just start and return
                logging.info("[Import Debug] Not waiting for app to be ready, returning immediately")
                return True
        except Exception as e:
            logging.error(f"[Import Debug] Exception during non-blocking reload: {e}", exc_info=True)
            return False

    def update_code(self, session_id: Optional[str], run_code: str) -> None:
        """
        Updates the running code and notifies the update.
        In order to notify of the update, the event loop and asyncio.Condition need
        to be aligned with the server's.
        """

        if self.mode != "edit":
            raise PermissionError("Cannot update code in non-edit mode.")
        if not self.is_app_process_server_ready.is_set():
            return
        self.run_code = run_code
        self.source_files = wf_project.build_source_files(self.app_path)
        self._clean_process()
        self._start_app_process()
        self.is_app_process_server_ready.wait()
        self.queue_announcement("codeUpdate", None)

    async def queue_announcement_async(
        self, type, payload, exclude_session_id: Optional[str] = None
    ):
        for session_id, announcement_queue in self.announcement_queues.items():
            if session_id == exclude_session_id:
                continue
            await announcement_queue.put({"type": type, "payload": payload})

    def queue_announcement(self, type, payload):
        async def announce(type: str, payload: Any):
            for announcement_queue in self.announcement_queues.values():
                await announcement_queue.put({"type": type, "payload": payload})

        if self.serve_loop is not None:
            try:
                future = asyncio.run_coroutine_threadsafe(announce(type, payload), self.serve_loop)
                future.result(AppRunner.MAX_WAIT_NOTIFY_SECONDS)
            except (
                RuntimeError,
                concurrent.futures.CancelledError,
                concurrent.futures.TimeoutError,
            ):
                # Ignore errors that occur during pytest runs where serve_loop may be closed
                pass

    def set_userinfo(self, session_id: str, userinfo: dict) -> None:
        def run_async_in_thread():
            message = AppProcessServerRequest(type="setUserinfo", payload=userinfo)

            asyncio.run(self.dispatch_message(session_id, message))

        thread = threading.Thread(target=run_async_in_thread)
        thread.start()
        thread.join()
        return

    def _subscribe_terminal_signal(self):
        def signal_handler(sig, frame):
            self.shut_down()
            sys.exit(0)

        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except ValueError:
            # No need to handle signal as not main thread
            pass
