from unittest.mock import ANY

import fastapi
import fastapi.testclient
import pytest
import writer.serve
from writer.app_runner import AppRunner
from writer.ss_types import EventRequest, WriterEvent

from tests.backend import test_app_dir
from tests.backend.fixtures.app_runner_fixtures import init_app_session


class TestJournal:
    proposed_session_id = "c13a280fe17ec663047ec14de15cd93ad686fecf5f9a4dbf262d3a86de8cb577"

    def test_api_entry(self, mock_kv_storage):
        asgi_app = writer.serve.get_asgi_app(test_app_dir, "run")
        blueprint_id = "m4gycroojx6am4cq"

        with fastapi.testclient.TestClient(asgi_app) as client:
            with client.stream(
                "POST",
                f"/private/api/blueprint/{blueprint_id}",
                json={"proposedSessionId": None},
                headers={"Content-Type": "application/json"},
            ) as response:
                assert response.status_code == 200

        assert len(mock_kv_storage._data_storage) == 1
        entry = mock_kv_storage._data_storage.values()[0]
        assert entry == {
            "timestamp": ANY,
            "instanceType": "agent",
            "blueprintId": "m4gycroojx6am4cq",
            "trigger": {
                "event": "wf-run-blueprint-via-api",
                "payload": {"proposedSessionId": None},
                "component": {"type": "block", "id": "qfqpqmjdpzuu8fe9", "title": "API alias"},
                "type": "API",
            },
            "blockOutputs": {
                "qfqpqmjdpzuu8fe9": {
                    "component": {
                        "type": "blueprints_apitrigger",
                        "id": "qfqpqmjdpzuu8fe9",
                        "title": "API alias",
                        "category": "Triggers",
                    },
                    "executions": [
                        {
                            "result": {"proposedSessionId": None},
                            "outcome": "trigger",
                            "startedAt": ANY,
                            "executionTimeInSeconds": ANY,
                        }
                    ],
                },
                "pa448833kc2pis3a": {
                    "component": {
                        "type": "blueprints_logmessage",
                        "id": "pa448833kc2pis3a",
                        "title": "Log message",
                        "category": "Other",
                    },
                    "executions": [
                        {
                            "result": "AAA",
                            "outcome": "success",
                            "startedAt": ANY,
                            "executionTimeInSeconds": ANY,
                        }
                    ],
                },
            },
            "isRunable": True,
            "result": "success",
        }

    def test_cron_entry(self, mock_kv_storage):
        asgi_app = writer.serve.get_asgi_app(test_app_dir, "run")
        blueprint_id = "m4gycroojx6am4cq"
        branch_id = "3abex827umkt4tuo"

        with fastapi.testclient.TestClient(asgi_app) as client:
            with client.stream(
                "POST",
                f"/private/api/blueprint/{blueprint_id}?branch_id={branch_id}",
                json={"proposedSessionId": None},
                headers={"Content-Type": "application/json"},
            ) as response:
                assert response.status_code == 200

        assert len(mock_kv_storage._data_storage) == 1
        entry = mock_kv_storage._data_storage.values()[0]
        assert entry == {
            "timestamp": ANY,
            "instanceType": "agent",
            "blueprintId": "m4gycroojx6am4cq",
            "trigger": {
                "event": "wf-run-blueprint-via-api",
                "payload": {"proposedSessionId": None},
                "component": {
                    "type": "block",
                    "id": "3abex827umkt4tuo",
                    "title": "my cron trigger",
                },
                "type": "Cron",
            },
            "blockOutputs": ANY,
            "isRunable": True,
            "result": "success",
        }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_ui_entry(self, setup_app_runner, mock_kv_storage):
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
                        {"componentId": "ud24upgqyxrjmh9q", "instanceNumber": 0},
                    ],
                    payload={},
                ),
            )

            await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert len(mock_kv_storage._data_storage) == 1
            entry = mock_kv_storage._data_storage.values()[0]
            assert entry == {
                "timestamp": ANY,
                "instanceType": "editor",
                "blueprintId": "m4gycroojx6am4cq",
                "trigger": {
                    "event": "wf-click",
                    "payload": {"ctrl_key": False, "shift_key": False, "meta_key": False},
                    "component": {"type": "block", "id": "kiwqzy0ftd62y912", "title": "UI Trigger"},
                    "type": "UI",
                },
                "blockOutputs": ANY,
                "isRunable": True,
                "result": "success",
            }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_ui_entry_return_value(self, setup_app_runner, mock_kv_storage):
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
                        {"componentId": "4quhc4plo1oa6vwz", "instanceNumber": 0},
                    ],
                    payload={},
                ),
            )

            await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert len(mock_kv_storage._data_storage) == 1
            entry = mock_kv_storage._data_storage.values()[0]
            assert entry == {
                "timestamp": ANY,
                "instanceType": "agent",
                "blueprintId": "m4gycroojx6am4cq",
                "trigger": {
                    "event": "wf-click",
                    "payload": {"ctrl_key": False, "shift_key": False, "meta_key": False},
                    "component": {"type": "block", "id": "6o0ev5lml7kpb6ii", "title": ""},
                    "type": "UI",
                },
                "blockOutputs": ANY,
                "isRunable": True,
                "result": "success",
            }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_on_demand_branch(self, setup_app_runner, mock_kv_storage):
        ar: AppRunner
        with setup_app_runner(test_app_dir, "edit", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)

            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-run-blueprint-branch",
                    isSafe=True,
                    instancePath=None,
                    handler="run_blueprint_branch",
                    payload={"branch_id": "6o0ev5lml7kpb6ii"},
                ),
            )

            await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert len(mock_kv_storage._data_storage) == 1
            entry = mock_kv_storage._data_storage.values()[0]
            assert entry == {
                "timestamp": ANY,
                "instanceType": "editor",
                "blueprintId": "m4gycroojx6am4cq",
                "trigger": {
                    "event": "wf-run-blueprint-branch",
                    "payload": {},
                    "component": {"type": "block", "id": "6o0ev5lml7kpb6ii", "title": ""},
                    "type": "On demand",
                },
                "blockOutputs": ANY,
                "isRunable": True,
                "result": "success",
            }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_on_demand_blueprint(self, setup_app_runner, mock_kv_storage):
        ar: AppRunner
        with setup_app_runner(test_app_dir, "edit", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)

            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-run-blueprint",
                    isSafe=True,
                    instancePath=None,
                    handler="run_blueprint_by_id",
                    payload={"blueprint_id": "m4gycroojx6am4cq"},
                ),
            )

            await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert len(mock_kv_storage._data_storage) == 1
            entry = mock_kv_storage._data_storage.values()[0]
            assert entry == {
                "timestamp": ANY,
                "instanceType": "editor",
                "blueprintId": "m4gycroojx6am4cq",
                "trigger": {
                    "event": "wf-run-blueprint",
                    "payload": {},
                    "component": {
                        "type": "blueprint",
                        "id": "m4gycroojx6am4cq",
                        "title": "journal",
                    },
                    "type": "On demand",
                },
                "blockOutputs": ANY,
                "isRunable": True,
                "result": "success",
            }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("setup_app_runner")
    async def test_on_demand_blueprint_error(self, setup_app_runner, mock_kv_storage):
        ar: AppRunner
        with setup_app_runner(test_app_dir, "edit", load=True) as ar:
            await init_app_session(ar, session_id=self.proposed_session_id)
            ev_req = EventRequest(
                type="event",
                payload=WriterEvent(
                    type="wf-run-blueprint",
                    isSafe=True,
                    instancePath=None,
                    handler="run_blueprint_by_id",
                    payload={"blueprint_id": "n5tm1c8il2kpzttw"},
                ),
            )

            await ar.dispatch_message(self.proposed_session_id, ev_req)
            assert len(mock_kv_storage._data_storage) == 1
            entry = mock_kv_storage._data_storage.values()[0]
            assert entry == {
                "timestamp": ANY,
                "instanceType": "editor",
                "blueprintId": "n5tm1c8il2kpzttw",
                "trigger": {
                    "event": "wf-run-blueprint",
                    "payload": {},
                    "component": {
                        "type": "blueprint",
                        "id": "n5tm1c8il2kpzttw",
                        "title": "THROW ERROR",
                    },
                    "type": "On demand",
                },
                "blockOutputs": ANY,
                "isRunable": True,
                "result": "error",
            }
