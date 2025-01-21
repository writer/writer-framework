
import asyncio
from pathlib import Path
import threading

import pytest
from tests.backend import parse_instance_path
from writer.app_runner import AppRunner
from writer.ss_types import (
    EventRequest,
    InitSessionRequest,
    InitSessionRequestPayload,
    WriterEvent,
)

from backend.fixtures.app_runner_fixtures import init_app_session
test_app_dir = Path(__file__).resolve().parent / "basic_test_app"

class TestAppRunner:

    proposed_session_id = "c13a280fe17ec663047ec14de15cd93ad686fecf5f9a4dbf262d3a86de8cb577"

    @pytest.mark.usefixtures("setup_app_runner")
    def test_init_wrong_path(self, setup_app_runner) -> None:
        with setup_app_runner("./not_an_app", "run") as ar:
            with pytest.raises(SystemExit) as wrapped_e:
                ar.load()
            assert wrapped_e.type == SystemExit

    def test_init_wrong_mode(self) -> None:
        with pytest.raises(ValueError):
            AppRunner(test_app_dir, "virus")

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_init_should_not_load_workflow_component_in_run_mode(self, setup_app_runner) -> None:
        ar: AppRunner
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            response = await ar.init_session(InitSessionRequestPayload(
                cookies={},
                headers={},
                proposedSessionId=self.proposed_session_id
            ))
            assert response.payload.components.get("workflows_root") is None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_init_should_load_workflow_component_in_edit_mode(self, setup_app_runner) -> None:
        ar: AppRunner
        with setup_app_runner(test_app_dir, "edit", load = True) as ar:
            response = await ar.init_session(InitSessionRequestPayload(
                cookies={},
                headers={},
                proposedSessionId=self.proposed_session_id
            ))

            assert response.payload.components.get("workflows_root") is not None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_backend_ui_event_should_not_load_workflow_component_in_run_mode(self, setup_app_runner) -> None:
        ar: AppRunner
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)

            ev_req = EventRequest(type="event", payload=WriterEvent(
                type="wf-click",
                instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,oue5vcsaz9bd69qp:0")
            ))

            rev = await ar.dispatch_message(self.proposed_session_id, ev_req)

            assert rev.payload.components.get("workflows_root") is None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_backend_ui_event_should_load_workflow_component_in_edit_mode(self, setup_app_runner) -> None:
        ar: AppRunner
        with setup_app_runner(test_app_dir, "edit", load = True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)

            ev_req = EventRequest(type="event", payload=WriterEvent(
                type="wf-click",
                instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,oue5vcsaz9bd69qp:0"),
                payload={}
            ))

            rev = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert rev.payload.components.get("workflows_root") is not None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_pre_session(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            er = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="virus",
                    instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,wdbiq88bn31by8yc:0"),
                    payload={"virus": "yes"}
                )
            )
            r = await ar.dispatch_message(None,  er)
            assert r.status == "error"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_valid_session_invalid_event(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            er = EventRequest(type="event", payload=WriterEvent(
                type="virus",
                instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,wdbiq88bn31by8yc:0"),
                payload={"virus": "yes"}
            ))
            rev = await ar.dispatch_message(None,  er)
            assert rev.status == "error"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_valid_event(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(type="event", payload=WriterEvent(
                type="wf-number-change",
                instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,wdbiq88bn31by8yc:0"),
                payload="129673"
            ))
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert ev_res.status == "ok"
            assert ev_res.payload.result.get("ok")
            expected_label = "Pet count: 129673.0"
            text_instance_path = "root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,n29p68fdi2r8ddyb:0"
            assert ev_res.payload.evaluatedTree.get(text_instance_path)["content"]["text"] == expected_label

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_async_handler(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(type="event", payload=WriterEvent(
                type="wf-click",
                instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,n0b3lkn4xz819zeo:0")
            ))
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert ev_res.status == "ok"
            assert ev_res.payload.result.get("ok")

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_bad_event_handler(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(type="event", payload=WriterEvent(
                type="wf-click",
                instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,gvbsltzfn85oa8lb:0"),
                payload={}
            ))
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert ev_res.status == "ok"
            assert not ev_res.payload.result.get("ok")

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_unsafe_event(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(type="event", payload=WriterEvent(
                type="wf-built-run",
                handler="nineninenine",
                instancePath=None,
                payload=None
            ))
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert ev_res.status == "ok"
            assert not ev_res.payload.result.get("ok")

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_safe_global_event(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load = True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(type="event", payload=WriterEvent(
                type="wf-built-run",
                isSafe=True,
                handler="nineninenine",
                instancePath=None,
                payload=None
            ))
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert ev_res.status == "ok"
            assert ev_res.payload.result.get("result") == 999

    @pytest.mark.usefixtures("setup_app_runner")
    def test_run_code_edit(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run") as ar:
            with pytest.raises(PermissionError):
                ar.update_code(None, "exec(virus)")
            with pytest.raises(PermissionError):
                ar.save_code(None, "exec(virus)")

    def run_loader_thread(self, app_runner: AppRunner) -> None:
        app_runner.update_code(None, "pet_count = 728")

    async def wait_for_code_update(self, app_runner: AppRunner) -> None:
        await app_runner.code_update_condition.acquire()
        try:
            await app_runner.code_update_condition.wait()
        finally:
            app_runner.code_update_condition.release()
        return True

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_code_update(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "edit") as ar:
            ar.hook_to_running_event_loop()
            ar.load()
            wait_update_task = asyncio.create_task(self.wait_for_code_update(ar))
            loader_thread = threading.Thread(target=self.run_loader_thread, args=(ar,))
            loader_thread.start()
            code_update_result = await wait_update_task
            loader_thread.join()

            assert code_update_result == True

            si = InitSessionRequest(
                type="sessionInit",
                payload=InitSessionRequestPayload(
                    cookies={},
                    headers={},
                    proposedSessionId=self.proposed_session_id
                )
            )
            si_res = await ar.dispatch_message(None, si)

            assert si_res.payload.evaluatedTree["root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,n29p68fdi2r8ddyb:0"]["content"]["text"] == "Pet count: 728"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_handle_event_should_return_result_of_event_handler_execution(self, setup_app_runner):
        """
        Tests that an event handler should result the result of function execution in
        payload.result["result"].
        """
        # Given
        ar: AppRunner
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            session_id = await init_app_session(ar)
            res = await ar.handle_event(session_id, WriterEvent(
                type="wf-click",
                instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,pxj7kbq7bca6e11g:0"),
                payload={})
            )
            assert res.payload.result["result"] == 999
