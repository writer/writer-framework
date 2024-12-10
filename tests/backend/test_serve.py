import mimetypes
import os

import fastapi
import fastapi.testclient
import pytest
from writer import crypto
import writer.abstract
import writer.serve
from fastapi import FastAPI

from tests.backend import test_app_dir, test_multiapp_dir


class TestServe:

    def test_valid(self) -> None:
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json"
            })
            assert res.status_code == 200
            session_id = res.json().get("sessionId")
            assert session_id is not None
            with client.websocket_connect("/api/stream") as websocket:
                websocket.send_json({
                    "type": "streamInit",
                    "trackingId": 0,
                    "payload": {
                        "sessionId": session_id
                    }
                })
                websocket.send_json({
                    "type": "event",
                    "trackingId": 1,
                    "payload": {
                        "type": "wf-number-change",
                        "instancePath": [
                            {"componentId": "root", "instanceNumber": 0}
                        ],
                        "payload": 9
                    }
                })
                a = websocket.receive_json()
                assert a.get("messageType") == "eventResponse"
                websocket.close(1000)

    def test_bad_session(self) -> None:
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            with client.websocket_connect("/api/stream") as websocket:
                websocket.send_json({
                    "type": "streamInit",
                    "trackingId": 0,
                    "payload": {
                        "sessionId": "bad_session"
                    }
                })
                with pytest.raises(fastapi.WebSocketDisconnect):
                    websocket.receive_json()

    def test_session_verifier_header(self) -> None:
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json",
                "X-Fail": "yes"
            })
            assert res.status_code == 403

    def test_session_verifier_cookies(self) -> None:
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app, cookies={
            "fail_cookie": "yes"
        }) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json"
            })
            assert res.status_code == 403

    def test_session_verifier_pass(self) -> None:
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app, cookies={
            "another_cookie": "yes"
        }) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json",
                "X-Success": "yes"
            })
            assert res.status_code == 200

    def test_serve_javascript_file_with_a_valid_content_type(self) -> None:
        # Arrange
        mimetypes.add_type("text/plain", ".js")

        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            # Acts
            res = client.get("/static/file.js")

            # Assert
            assert res.status_code == 200
            assert res.headers["Content-Type"].startswith("text/javascript")

    def test_multiapp_should_run_the_lifespan_of_all_writer_app(self):
        """
        This test check that multiple Writer Framework applications embedded
        in FastAPI start completely and answer websocket request.
        """
        asgi_app: fastapi.FastAPI = FastAPI(lifespan=writer.serve.lifespan)
        asgi_app.mount("/app1", writer.serve.get_asgi_app(test_multiapp_dir / 'app1', "run"))
        asgi_app.mount("/app2", writer.serve.get_asgi_app(test_multiapp_dir / 'app2', "run"))

        with fastapi.testclient.TestClient(asgi_app) as client:
            # test websocket connection on app1
            with client.websocket_connect("/app1/api/stream") as websocket:
                websocket.send_json({
                    "type": "streamInit",
                    "trackingId": 0,
                    "payload": {
                        "sessionId": "bad_session"
                    }
                })
                with pytest.raises(fastapi.WebSocketDisconnect):
                    websocket.receive_json()

            # test websocket connection on app2
            with client.websocket_connect("/app2/api/stream") as websocket:
                websocket.send_json({
                    "type": "streamInit",
                    "trackingId": 0,
                    "payload": {
                        "sessionId": "bad_session"
                    }
                })
                with pytest.raises(fastapi.WebSocketDisconnect):
                    websocket.receive_json()

    def test_server_setup_hook_is_executed_when_its_present_and_enabled(self):
        """
        This test verifies that the server_setup.py hook is executed when the application
        is started with the enable_server_setup=True option.

        """
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(test_app_dir, "run", enable_server_setup=True)
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.get("/probes/healthcheck")
            assert res.status_code == 200
            assert res.text == '"1"'

    def test_server_setup_hook_is_ignored_when_its_disabled(self):
        """
        This test verifies that the server_setup.py hook is not executed
        when the application is started by disabling the server_setup.py hook.

        """
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(test_app_dir, "run", enable_server_setup=False)
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.get("/probes/healthcheck")
            assert res.status_code == 404

    def test_abstract_components(self):
        writer.abstract.register_abstract_template("sectiona", {
            "baseType": "section",
            "writer": {
                "name": "Section A"
            }
        })
        writer.abstract.register_abstract_template("columnb", {
            "baseType": "column",
            "writer": {
                "description": "Cloned Column component"
            }
        })

        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json"
            })
            abstract_templates = res.json().get("abstractTemplates")
            section_a = abstract_templates.get("sectiona")
            column_b = abstract_templates.get("columnb")
            assert section_a.get("writer").get("name") == "Section A"
            assert column_b.get("writer").get("description") == "Cloned Column component"
          
    def test_feature_flags(self):
        """
        This test verifies that feature flags are carried to the frontend.

        """
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json"
            })
            feature_flags = res.json().get("featureFlags")
            assert feature_flags == ["flag_one", "flag_two"]

    # def test_create_workflow_job_api(self):
    #     asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(
    #         test_app_dir, "run")
    #     os.environ["WRITER_BASE_HASH"] = "abc"
    #     workflow_key = "workflow2"
        
    #     with fastapi.testclient.TestClient(asgi_app) as client:
    #         create_job_token = crypto.get_hash(f"create_job_{workflow_key}")
    #         res = client.post(f"/api/job/workflow/{workflow_key}", json={
    #             "proposedSessionId": None
    #         }, headers={
    #             "Content-Type": "application/json",
    #             "Authorization": f"Bearer {create_job_token}"
    #         })
    #         job_id = res.json().get("id")
    #         get_job_token = res.json().get("token")
    #         res = client.get(f"/api/job/{job_id}", headers={
    #             "Authorization": f"Bearer {get_job_token}"
    #         })
    #         assert res.json().get("result") == 987127

    #     os.environ["WRITER_BASE_HASH"] = ""

