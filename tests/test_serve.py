import json
import mimetypes

import fastapi
import streamsync.serve
import fastapi.testclient
import pytest

from tests import test_app_dir


class TestServe:

    def test_valid(self) -> None:
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
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
                        "type": "ss-number-change",
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
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
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
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
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
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
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
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
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

        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            # Acts
            res = client.get("/static/file.js")

            # Assert
            assert res.status_code == 200
            assert res.headers["Content-Type"].startswith("text/javascript")
