import asyncio
import threading

import pytest
from writer.app_runner import AppRunner
from writer.ss_types import (
    EventRequest,
    InitSessionRequest,
    InitSessionRequestPayload,
    WriterEvent,
)

from backend.fixtures.app_runner_fixtures import init_app_session
from tests.backend import test_app_dir


class TestAppRunner:
    numberinput_instance_path = [
        {"componentId": "root", "instanceNumber": 0},
        {"componentId": "7730df5b-8731-4123-bacc-898e7347b124", "instanceNumber": 0},
        {"componentId": "6010765e-9ac3-4570-84bf-913ae404e03a", "instanceNumber": 0},
        {"componentId": "c282ad31-2487-4296-a944-508c167c43be", "instanceNumber": 0},
    ]

    async_handler_click_path = [
        {"componentId": "root", "instanceNumber": 0},
        {"componentId": "bb4d0e86-619e-4367-a180-be28ab6059f4", "instanceNumber": 0},
        {"componentId": "92a2c0c8-7ab4-4865-b7eb-ed437408c8f5", "instanceNumber": 0},
        {"componentId": "d1e01ce1-fab1-4a6e-91a1-1f45f9e57aa5", "instanceNumber": 0},
        {"componentId": "9c30af6d-4ee5-4782-9169-0f361d67fa76", "instanceNumber": 0},
        {"componentId": "nyo5vc79sb031yz8", "instanceNumber": 0},
    ]
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
    async def test_init_should_not_load_blueprint_component_in_run_mode(
        self, setup_app_runner
    ) -> None:
        ar: AppRunner
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            response = await ar.init_session(
                InitSessionRequestPayload(
                    cookies={}, headers={}, proposedSessionId=self.proposed_session_id
                )
            )

            assert response.payload.components.get("blueprints_root") is None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_init_should_load_blueprint_component_in_edit_mode(self, setup_app_runner) -> None:
        ar: AppRunner
        with setup_app_runner(test_app_dir, "edit", load=True) as ar:
            response = await ar.init_session(
                InitSessionRequestPayload(
                    cookies={}, headers={}, proposedSessionId=self.proposed_session_id
                )
            )

            assert response.payload.components.get("blueprints_root") is not None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_backend_ui_event_should_not_load_blueprint_component_in_run_mode(
        self, setup_app_runner
    ) -> None:
        ar: AppRunner
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)

            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-click",
                    instancePath=[
                        {"componentId": "root", "instanceNumber": 0},
                        {
                            "componentId": "bb4d0e86-619e-4367-a180-be28ab6059f4",
                            "instanceNumber": 0,
                        },
                        {
                            "componentId": "92a2c0c8-7ab4-4865-b7eb-ed437408c8f5",
                            "instanceNumber": 0,
                        },
                        {
                            "componentId": "d1e01ce1-fab1-4a6e-91a1-1f45f9e57aa5",
                            "instanceNumber": 0,
                        },
                        {
                            "componentId": "9c30af6d-4ee5-4782-9169-0f361d67fa76",
                            "instanceNumber": 0,
                        },
                        {"componentId": "8ykyk5avd9ioyr6l", "instanceNumber": 0},
                    ],
                    payload={},
                ),
            )

            rev = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert rev.payload.components.get("blueprints_root") is None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_backend_ui_event_should_load_blueprint_component_in_edit_mode(
        self, setup_app_runner
    ) -> None:
        ar: AppRunner
        with setup_app_runner(test_app_dir, "edit", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)

            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-click",
                    instancePath=[
                        {"componentId": "root", "instanceNumber": 0},
                        {
                            "componentId": "bb4d0e86-619e-4367-a180-be28ab6059f4",
                            "instanceNumber": 0,
                        },
                        {
                            "componentId": "92a2c0c8-7ab4-4865-b7eb-ed437408c8f5",
                            "instanceNumber": 0,
                        },
                        {
                            "componentId": "d1e01ce1-fab1-4a6e-91a1-1f45f9e57aa5",
                            "instanceNumber": 0,
                        },
                        {
                            "componentId": "9c30af6d-4ee5-4782-9169-0f361d67fa76",
                            "instanceNumber": 0,
                        },
                        {"componentId": "8ykyk5avd9ioyr6l", "instanceNumber": 0},
                    ],
                    payload={},
                ),
            )

            rev = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert rev.payload.components.get("blueprints_root") is not None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_pre_session(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            er = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="virus",
                    instancePath=self.numberinput_instance_path,
                    payload={"virus": "yes"},
                ),
            )
            r = await ar.dispatch_message(None, er)
            assert r.status == "error"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_valid_session_invalid_event(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            er = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="virus",
                    instancePath=self.numberinput_instance_path,
                    payload={"virus": "yes"},
                ),
            )
            rev = await ar.dispatch_message(None, er)
            assert rev.status == "error"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_valid_event(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-number-change",
                    instancePath=self.numberinput_instance_path,
                    payload="129673",
                ),
            )
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert ev_res.status == "ok"
            assert ev_res.payload.result.get("ok")
            assert ev_res.payload.mutations.get("+inspected_payload") == "129673.0"
            assert ev_res.payload.mutations.get("+b.pet_count") == 129673

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_async_handler(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            # Firing an event to bypass "initial" state mutations
            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-number-change",
                    instancePath=self.numberinput_instance_path,
                    payload="129673",
                ),
            )
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)

            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(type="wf-click", instancePath=self.async_handler_click_path),
            )
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert ev_res.status == "ok"
            assert ev_res.payload.result.get("ok")
            assert "+counter" in ev_res.payload.mutations

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_bad_event_handler(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            bad_button_instance_path = [
                {"componentId": "root", "instanceNumber": 0},
                {"componentId": "28a2212b-bc58-4398-8a72-2554e5296490", "instanceNumber": 0},
                {"componentId": "232d749a-5e0c-4802-bbe1-f8cae06db112", "instanceNumber": 0},
            ]
            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="click", instancePath=bad_button_instance_path, payload={}
                ),
            )
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            print(repr(ev_res))
            assert ev_res.status == "ok"
            assert not ev_res.payload.result.get("ok")

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_unsafe_event(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-built-run", handler="nineninenine", instancePath=None, payload=None
                ),
            )
            ev_res = await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert ev_res.status == "ok"
            assert not ev_res.payload.result.get("ok")

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_safe_global_event(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-built-run",
                    isSafe=True,
                    handler="nineninenine",
                    instancePath=None,
                    payload=None,
                ),
            )
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
        app_runner.update_code(None, "print('188542')")

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_code_update(self, setup_app_runner) -> None:
        with setup_app_runner(test_app_dir, "edit") as ar:
            ar.hook_to_running_event_loop()
            ar.load()
            aq = asyncio.Queue()
            ar.announcement_queues["dummy_session"] = aq
            loader_thread = threading.Thread(target=self.run_loader_thread, args=(ar,))
            loader_thread.start()
            await aq.get()
            loader_thread.join()
            del ar.announcement_queues["dummy_session"]

            si = InitSessionRequest(
                type="sessionInit",
                payload=InitSessionRequestPayload(
                    cookies={}, headers={}, proposedSessionId=self.proposed_session_id
                ),
            )
            si_res = await ar.dispatch_message(None, si)
            mail = list(si_res.payload.model_dump().get("mail"))

            assert mail[0].get("payload").get("message") == "188542\n"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_handle_event_should_return_result_of_event_handler_execution(
        self, setup_app_runner
    ):
        """
        Tests that an event handler should result the result of function execution in
        payload.result['result'].
        """
        # Given
        ar: AppRunner
        with setup_app_runner(test_app_dir, "run", load=True) as ar:
            session_id = await init_app_session(ar)

            # When
            res = await ar.handle_event(
                session_id,
                WriterEvent(
                    type="click",
                    instancePath=[
                        {"componentId": "5c0df6e8-4dd8-4485-a244-8e9e7f4b4675", "instanceNumber": 0}
                    ],
                    payload={},
                ),
            )

            # Then
            assert res.payload.result["result"] is not None
