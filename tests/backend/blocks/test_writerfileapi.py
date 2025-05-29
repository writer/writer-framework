from datetime import datetime as dt

import pytest
from writer.blocks.writerfileapi import WriterUploadFile
from writer.ss_types import WriterConfigurationError


# ---------------------------
# Shared test helpers
# ---------------------------
class MockFile:
    def __init__(self):
        self.id = "file-123"
        self.name = "myfile.pdf"
        self.status = "processed"
        self.created_at = dt.strptime("2024-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        self.graph_ids = ["g1", "g2"]


class MockDownloadResponse:
    def read(self):
        return b"file-bytes"


# ---------------------------
# Upload
# ---------------------------
def test_upload_file(monkeypatch, session, runner):
    class MockClient:
        class files:
            @staticmethod
            def upload(content, content_type, content_disposition):
                assert content == "some text"
                assert content_type == "text/plain"
                assert "my.txt" in content_disposition
                return MockFile()

    monkeypatch.setattr(
        "writer.ai.WriterAIManager.acquire_client",
        lambda custom_httpx_client=None, force_new_client=False: MockClient()
    )
    component = session.add_fake_component({"files": '[{"data": "some text", "type": "text/plain", "name": "my.txt"}]'})
    block = WriterUploadFile(component, runner, {})
    block.run()

    assert block.outcome == "success"
    assert block.result[0]["id"] == "file-123"


def test_upload_file_missing_field(session, runner, fake_client):
    component = session.add_fake_component({"files": '[{"type": "text/plain", "name": "my.txt"}]'})
    block = WriterUploadFile(component, runner, {})
    with pytest.raises(ValueError):
        block.run()


def test_upload_file_sdk_error(monkeypatch, session, runner):
    class MockClient:
        class files:
            @staticmethod
            def upload(*args, **kwargs):
                raise RuntimeError("upload failed")

    monkeypatch.setattr(
        "writer.ai.WriterAIManager.acquire_client",
        lambda custom_httpx_client=None, force_new_client=False: MockClient()
    )
    component = session.add_fake_component({"files": '[{"data": "some text", "type": "text/plain", "name": "my.txt"}]'})
    block = WriterUploadFile(component, runner, {})
    with pytest.raises(RuntimeError):
        block.run()
    assert block.outcome == "error"
