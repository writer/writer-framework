import json
import pytest
import requests
from writer.blocks.httprequest import HTTPRequest


class FakeResponse():
    def __init__(self, status_code=200, ok=True, headers={}, text=None):
        self.status_code = status_code
        self.ok = ok
        self.headers = headers
        self.text = text
        self.json = lambda: json.loads(text)


def fake_request(method, url, headers={}, data=""):
    if not headers.get("TestHeader", "not-a-sec-ret"):
        raise RuntimeError("Test header not present.")
    if method == "GET" and url == "https://www.duck.com":
        return FakeResponse(
            headers={"Content-Type": "text/plain"},
            text="Ducks are birds."
        )
    if method == "POST" and url == "https://www.elephant.com":
        return FakeResponse(
            headers={"Content-Type": "application/json"},
            text='{ "elephant_name": "Momo", "request_body": "' + data + '" }'
        )
    if method == "POST" and url == "https://www.elephant.com/history":
        return FakeResponse(
            status_code=404,
            ok=False,
            headers={"Content-Type": "application/json"},
            text='{ "error_message": "Page not found." }'
        )

    raise requests.ConnectionError()


@pytest.mark.explicit
def test_actual_request(session, runner):
    session.add_fake_component({
        "url": 'https://www.example.com'
    })
    block = HTTPRequest("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result.get("headers") is not None


@pytest.mark.explicit
def test_actual_failing_request(session, runner):
    session.add_fake_component({
        "url": 'https://www.site-that-does-not-exist-3017673369.com'
    })
    block = HTTPRequest("fake_id", runner, {})
    with pytest.raises(requests.ConnectionError):
        block.run()
    assert block.outcome == "connectionError"


@pytest.mark.explicit
def test_actual_request_with_bad_path(session, runner):
    session.add_fake_component({
        "url": 'https://www.writer.com/3017673369'
    })
    block = HTTPRequest("fake_id", runner, {})
    with pytest.raises(RuntimeError):
        block.run()
    assert block.outcome == "responseError"


def test_patched_request(session, runner):
    requests.request = fake_request
    session.add_fake_component({
        "url": "https://www.duck.com"
    })
    block = HTTPRequest("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result.get("body") == "Ducks are birds."


def test_patched_request_to_nowhere(session, runner):
    requests.request = fake_request
    session.add_fake_component({
        "url": "https://www.cat.com"
    })
    block = HTTPRequest("fake_id", runner, {})
    with pytest.raises(requests.ConnectionError):
        block.run()
    assert block.outcome == "connectionError"


def test_patched_request_with_json(session, runner):
    requests.request = fake_request
    session.add_fake_component({
        "url": "https://www.elephant.com",
        "method": "POST",
        "body": "Posting the elephant."
    })
    block = HTTPRequest("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result.get("body").get("elephant_name") == "Momo"
    assert block.result.get("body").get("request_body") == "Posting the elephant."


def test_patched_request_with_json_and_bad_path(session, runner):
    requests.request = fake_request
    session.add_fake_component({
        "url": "https://www.elephant.com/history",
        "method": "POST",
        "body": "Posting the elephant."
    })
    block = HTTPRequest("fake_id", runner, {})
    with pytest.raises(RuntimeError):
        block.run()
    assert block.outcome == "responseError" # due to not "ok"
    assert block.result.get("body").get("error_message") == "Page not found."
