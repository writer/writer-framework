import fastapi
import fastapi.testclient
import pytest
import writer.serve
from writer import auth

from tests.backend import test_basicauth_dir


class TestAuth:

    def test_basicauth_authentication_module_should_ask_user_to_write_basic_auth(self):
        """
        This test verifies that a user has to authenticate when the basic auth module is active.

        """
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(test_basicauth_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.get("/api/init")
            assert res.status_code == 401

    def test_basicauth_authentication_module_should_accept_user_using_authorization(self):
        """
        This test verifies that a user can use the application when providing basic auth credentials.

        """
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(test_basicauth_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.get("/static/file.js", auth=("admin", "admin"))
            assert res.status_code == 200

    def test_basicauth_authentication_module_disabled_when_server_setup_hook_is_disabled(self):
        """
        This test verifies that a user bypass the authentication when server setup hook is disabled.
        """
        asgi_app: fastapi.FastAPI = writer.serve.get_asgi_app(test_basicauth_dir, "run", enable_server_setup=False)
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.get("/api/init")
            assert res.status_code == 405

    @pytest.mark.parametrize("path,expected_path", [
        ("", "/"),
        ("http://localhost", "/"),
        ("http://localhost/", "/"),
        ("http://localhost/any", "/any"),
        ("http://localhost/any/", "/any/")
    ])
    def test_url_path_scenarios(self, path: str, expected_path: str):
        assert auth.urlpath(path) == expected_path

    @pytest.mark.parametrize("path,expected_path", [
        ("/", ""),
        ("/yolo", "yolo"),
        ("/yolo/", "yolo"),
        ("http://localhost", "http://localhost"),
        ("http://localhost/", "http://localhost"),
        ("http://localhost/any", "http://localhost/any"),
        ("http://localhost/any/", "http://localhost/any")
    ])
    def test_url_split_scenarios(self, path: str, expected_path: str):
        assert auth.urlstrip(path) == expected_path

    @pytest.mark.parametrize("path1,path2,expected_path", [
        ("/", "any", "/any"),
        ("", "any", "any"),
        ("http://localhost", "any", "http://localhost/any"),
        ("http://localhost/", "/any", "http://localhost/any"),
        ("http://localhost/yolo", "/any", "http://localhost/yolo/any"),
    ])
    def test_urljoin_scenarios(self, path1: str, path2, expected_path: str):
        assert auth.urljoin(path1, path2) == expected_path
