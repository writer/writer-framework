import asyncio
import concurrent.futures
import importlib.util
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
import threading
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Union, cast

import watchdog.events
from pydantic import ValidationError
from watchdog.observers.polling import PollingObserver

from writer import VERSION, audit_and_fix, core_ui, crypto, wf_project
from writer.core import (
    Config,
    EventHandlerRegistry,
    MiddlewareRegistry,
    WriterSession,
    use_request_context,
)
from writer.core_ui import ingest_bmc_component_tree
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
    ServeMode,
    SourceFilesDirectory,
    StateContentRequest,
    StateContentResponsePayload,
    StateEnquiryRequest,
    StateEnquiryResponsePayload,
    WriterApplicationInformation,
    WriterEvent,
)
from writer.wf_project import WfProjectContext

logging.basicConfig(level=logging.INFO, format="%(message)s")


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

        writer_application: Optional[WriterApplicationInformation] = None
        writer_app_id = os.getenv("WRITER_APP_ID")
        writer_org_id = os.getenv("WRITER_ORG_ID")
        if writer_app_id is not None and writer_org_id is not None:
            writer_application = WriterApplicationInformation(
                id=writer_app_id, organizationId=writer_org_id
            )

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
                    }
                    for app in applications
                ]
                return AppProcessServerResponse(
                    status="ok", status_message=None, payload={"data": raw_apps}
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

            raise MessageHandlingException("Invalid event.")

    def _execute_user_code(self) -> None:
        """
        Executes the user code and captures standard output.
        """

        import io
        from contextlib import redirect_stdout

        import writer

        writeruserapp = sys.modules.get("writeruserapp")
        if writeruserapp is None:
            raise ValueError("Couldn't find app module (writeruserapp).")

        code_path = os.path.join(self.app_path, "main.py")
        with redirect_stdout(io.StringIO()) as f:
            code = compile(self.run_code, code_path, "exec")
            exec(code, writeruserapp.__dict__)
        captured_stdout = f.getvalue()

        if captured_stdout:
            writer.core.initial_state.add_log_entry(
                "info", "Stdout message during initialization", captured_stdout
            )

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
        while True:  # Starts app message server
            try:
                if not self.server_conn.poll(1):
                    continue
                packet = self.server_conn.recv()
                if packet is None:  # An empty packet terminates the process
                    # Send empty packet to client for it to close
                    terminate_server()
                    return
                self._handle_app_process_server_packet(packet)
            except InterruptedError:
                terminate_server()
                return
            except BaseException as e:
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
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=(os.cpu_count() or 4) * 10
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
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())

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
        logger = logging.getLogger("app")
        logger.addHandler(logging.handlers.QueueHandler(self.log_queue))
        self.log_listener = LogListener(self.log_queue)
        self.log_listener.start()

    def _start_fs_observer(self):
        self.observer = PollingObserver(AppRunner.UPDATE_CHECK_INTERVAL_SECONDS)
        self.observer.schedule(
            FileEventHandler(self.reload_code_from_saved, patterns=["*.py"]),
            path=self.app_path,
            recursive=True,
        )
        self.observer.schedule(
            FileEventHandler(self._install_requirements, patterns=["requirements.txt"]),
            path=self.app_path,
        )
        self.observer.start()

    def _start_wf_project_process_write_files(self):
        wf_project.start_process_write_files_async(
            self.wf_project_context, AppRunner.WF_PROJECT_SAVE_INTERVAL
        )

    def _install_requirements(self) -> None:
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
        except OSError as e:
            # If the error is due to the function not being implemented (like S3/Fuse), we fallback to copy/delete
            if e.errno == 38:
                shutil.copy2(from_path_abs, to_path_abs)
                os.remove(from_path_abs)
            else:
                raise e

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
            logger.error("Couldn't find %s in the path provided: %s.", file, self.app_path)
            if file == "main.py":
                sys.exit(1)
            else:
                raise error

    def _check_file_in_app_path(self, path):
        if not os.path.abspath(path).startswith(os.path.abspath((self.app_path))):
            raise PermissionError(f"{path} is outside of application ({self.app_path})")

    def _load_persisted_components(self) -> Dict[str, ComponentDefinition]:
        logger = logging.getLogger("writer")

        if not os.path.isfile(
            os.path.join(self.app_path, ".wf", "components-blueprints_root.jsonl")
        ):
            wf_project.create_default_blueprints_root(self.app_path)

        if not os.path.isdir(os.path.join(self.app_path, ".wf")):
            logger.error("Couldn't find .wf in the path provided: %s.", self.app_path)
            sys.exit(1)

        _, components = wf_project.read_files(self.app_path)
        components = audit_and_fix.fix_components(components)
        return components

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
        self.is_app_process_server_ready.wait()
        if self.mode == "run" and self.is_app_process_server_failed.is_set():
            self.shut_down()
            sys.exit(1)

    def reload_code_from_saved(self) -> None:
        if not self.is_app_process_server_ready.is_set():
            return
        self.update_code(None, self.load_persisted_script())

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
