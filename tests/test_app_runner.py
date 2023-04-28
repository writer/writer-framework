
from streamsync.app_runner import AppRunner
import pytest
from streamsync.ss_types import EventRequest, InitSessionRequest, InitSessionRequestPayload, StreamsyncEvent


class TestAppRunner:

    run_ar = AppRunner("./testapp", "run")
    edit_ar = AppRunner("./testapp", "edit")
    numberinput_instance_path = [
        {"componentId": "root", "instanceNumber": 0},
        {"componentId": "7730df5b-8731-4123-bacc-898e7347b124", "instanceNumber": 0},
        {"componentId": "6010765e-9ac3-4570-84bf-913ae404e03a", "instanceNumber": 0},
        {"componentId": "c282ad31-2487-4296-a944-508c167c43be", "instanceNumber": 0}
    ]
    proposed_session_id = "c13a280fe17ec663047ec14de15cd93ad686fecf5f9a4dbf262d3a86de8cb577"

    def test_init_wrong_path(self) -> None:
        ar = AppRunner("./not_an_app", "run")
        with pytest.raises(SystemExit) as wrapped_e:
            ar.load()
        assert wrapped_e.type == SystemExit

    def test_init_wrong_mode(self) -> None:
        with pytest.raises(ValueError):
            AppRunner("./testapp", "virus")

    @pytest.mark.asyncio
    async def test_pre_session(self) -> None:
        er = EventRequest(
            type="event",
            payload=StreamsyncEvent(
                type="virus",
                instancePath=self.numberinput_instance_path,
                payload={
                    "virus": "yes"
                }
            )
        )
        self.run_ar.load()
        r = await self.run_ar.dispatch_message(None,  er)
        assert r.status == "error"
        self.run_ar.shut_down()

    @pytest.mark.asyncio
    async def test_valid_session_invalid_event(self) -> None:
        self.run_ar.load()
        si = InitSessionRequest(
            type="sessionInit",
            payload=InitSessionRequestPayload(
                cookies={},
                headers={},
                proposedSessionId=self.proposed_session_id
            )
        )
        sres = await self.run_ar.dispatch_message(None, si)
        assert sres.status == "ok"
        assert sres.payload.dict().get("sessionId") == self.proposed_session_id
        er = EventRequest(type="event", payload=StreamsyncEvent(
            type="virus",
            instancePath=self.numberinput_instance_path,
            payload={
                "virus": "yes"
            }
        ))
        rev = await self.run_ar.dispatch_message(None,  er)
        assert rev.status == "error"
        self.run_ar.shut_down()

    @pytest.mark.asyncio
    async def test_valid_event(self) -> None:
        self.run_ar.load()
        si = InitSessionRequest(
            type="sessionInit",
            payload=InitSessionRequestPayload(
                cookies={},
                headers={},
                proposedSessionId=self.proposed_session_id
            )
        )
        sres = await self.run_ar.dispatch_message(None, si)
        assert sres.status == "ok"
        assert sres.payload.dict().get("sessionId") == self.proposed_session_id
        ev_req = EventRequest(type="event", payload=StreamsyncEvent(
            type="ss-number-change",
            instancePath=self.numberinput_instance_path,
            payload="129673"
        ))
        ev_res = await self.run_ar.dispatch_message(self.proposed_session_id, ev_req)
        assert ev_res.status == "ok"
        assert ev_res.payload.result.get("ok") == True
        assert ev_res.payload.mutations.get(
            "inspected_payload") == "129673.0"
        assert ev_res.payload.mutations.get(
            "b.pet_count") == 129673
        self.run_ar.shut_down()

    @pytest.mark.asyncio
    async def test_bad_event_handler(self) -> None:
        self.run_ar.load()
        si = InitSessionRequest(
            type="sessionInit",
            payload=InitSessionRequestPayload(
                cookies={},
                headers={},
                proposedSessionId=self.proposed_session_id
            )
        )
        await self.run_ar.dispatch_message(None, si)
        bad_button_instance_path = [
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "28a2212b-bc58-4398-8a72-2554e5296490", "instanceNumber": 0},
            {"componentId": "232d749a-5e0c-4802-bbe1-f8cae06db112", "instanceNumber": 0}
        ]
        ev_req = EventRequest(type="event", payload=StreamsyncEvent(
            type="click",
            instancePath=bad_button_instance_path,
            payload={}
        ))
        ev_res = await self.run_ar.dispatch_message(self.proposed_session_id, ev_req)
        print(repr(ev_res))
        assert ev_res.status == "ok"
        assert ev_res.payload.result.get("ok") == False
        self.run_ar.shut_down()

    def test_run_code_edit(self) -> None:
        with pytest.raises(PermissionError):
            self.run_ar.update_code(None, "exec(virus)")
        with pytest.raises(PermissionError):
            self.run_ar.save_code(None, "exec(virus)")

    @pytest.mark.asyncio
    async def test_code_update(self) -> None:
        self.edit_ar.load()
        self.edit_ar.update_code(None, "print('188542')")
        assert 1 == self.edit_ar.run_code_version

        si = InitSessionRequest(
            type="sessionInit",
            payload=InitSessionRequestPayload(
                cookies={},
                headers={},
                proposedSessionId=self.proposed_session_id
            )
        )
        si_res = await self.edit_ar.dispatch_message(None, si)
        mail = list(si_res.payload.dict().get("mail"))

        assert mail[0].get(
            "payload").get("message") == "188542\n"

        self.edit_ar.shut_down()
