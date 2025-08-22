import pytest
from writer.blocks.writeraddtokg import WriterAddToKG
from writer.ss_types import WriterConfigurationError


class MockFile:
    pass


class MockGraph:
    def add_file(self, file):
        assert isinstance(file, MockFile)
    
    def add_url(self, url):
        assert isinstance(url, str)
        assert url.startswith("http")


def mock_retrieve_graph(graph_id):
    assert graph_id == "abc123"
    return MockGraph()


def mock_upload_file(data, type, name):
    assert data == b"123"
    assert type == "application/pdf"
    assert name in ["interesting.pdf", "doc.pdf"]  # Accept both test filenames
    return MockFile()


def test_add_to_kg(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    monkeypatch.setattr("writer.ai.upload_file", mock_upload_file)

    session.session_state["my_files"] = [
        {"data": b"123", "type": "application/pdf", "name": "interesting.pdf"},
        {"data": b"123", "type": "application/pdf", "name": "interesting.pdf"},
    ]
    component = session.add_fake_component({"graphId": "abc123", "files": "@{my_files}", "urls": "[]"})
    block = WriterAddToKG(component, runner, {})
    block.run()
    assert block.outcome == "success"


def test_add_to_kg_missing_type(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    monkeypatch.setattr("writer.ai.upload_file", mock_upload_file)

    session.session_state["my_files"] = [{"data": b"123", "name": "interesting.pdf"}]
    component = session.add_fake_component({"graphId": "abc123", "files": "@{my_files}", "urls": "[]"})
    block = WriterAddToKG(component, runner, {})

    with pytest.raises(WriterConfigurationError):
        block.run()


def test_add_to_kg_wrong_type(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    monkeypatch.setattr("writer.ai.upload_file", mock_upload_file)

    session.session_state["my_files"] = "should be list"
    component = session.add_fake_component({"graphId": "abc123", "files": "@{my_files}", "urls": "[]"})
    block = WriterAddToKG(component, runner, {})

    with pytest.raises(WriterConfigurationError):
        block.run()


def test_add_urls_to_kg(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    
    session.session_state["my_urls"] = [
        "https://docs.python.org/3/",
        "https://www.python.org/about/"
    ]
    component = session.add_fake_component({
        "graphId": "abc123", 
        "files": "[]",
        "urls": "@{my_urls}"
    })
    block = WriterAddToKG(component, runner, {})
    block.run()
    assert block.outcome == "success"


def test_add_mixed_files_and_urls(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    monkeypatch.setattr("writer.ai.upload_file", mock_upload_file)
    
    session.session_state["my_files"] = [
        {"data": b"123", "type": "application/pdf", "name": "doc.pdf"}
    ]
    session.session_state["my_urls"] = ["https://example.com"]
    
    component = session.add_fake_component({
        "graphId": "abc123", 
        "files": "@{my_files}",
        "urls": "@{my_urls}"
    })
    block = WriterAddToKG(component, runner, {})
    block.run()
    assert block.outcome == "success"


def test_add_to_kg_no_content(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    
    component = session.add_fake_component({
        "graphId": "abc123", 
        "files": "[]",
        "urls": "[]"
    })
    block = WriterAddToKG(component, runner, {})
    
    with pytest.raises(WriterConfigurationError, match="At least one file or URL must be provided"):
        block.run()


def test_add_to_kg_invalid_urls(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    
    session.session_state["invalid_urls"] = [123, "not a string"]
    component = session.add_fake_component({
        "graphId": "abc123", 
        "files": "[]",
        "urls": "@{invalid_urls}"
    })
    block = WriterAddToKG(component, runner, {})
    
    with pytest.raises(WriterConfigurationError, match="URL must be a string"):
        block.run()
