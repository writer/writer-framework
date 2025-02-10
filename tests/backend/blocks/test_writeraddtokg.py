import pytest
import writer.ai
from writer.blocks.writeraddtokg import WriterAddToKG
from writer.ss_types import WriterConfigurationError


class MockFile():
    pass

class MockGraph():

    def add_file(self, file):
        assert isinstance(file, MockFile)

def mock_retrieve_graph(graph_id):
    assert graph_id == "abc123"
    return MockGraph()

def mock_upload_file(data, type, name):
    assert data == b"123"
    assert type == "application/pdf"
    assert name == "interesting.pdf"
    return MockFile()


def test_add_to_kg(monkeypatch, session, runner):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    monkeypatch.setattr("writer.ai.upload_file", mock_upload_file)

    session.state.my_files = [
        {
            "data": b"123",
            "type": "application/pdf",
            "name": "interesting.pdf"
        },
        {
            "data": b"123",
            "type": "application/pdf",
            "name": "interesting.pdf"
        }
    ]
    session.add_fake_component({
        "graphId": "abc123",
        "files": "{{my_files}}"
    })
    block = WriterAddToKG("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"


def test_add_to_kg_missing_type(monkeypatch, session, runner):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    monkeypatch.setattr("writer.ai.upload_file", mock_upload_file)

    session.state.my_files = [
        {
            "data": b"123",
            "name": "interesting.pdf"
        }
    ]
    session.add_fake_component({
        "graphId": "abc123",
        "files": "{{my_files}}"
    })
    block = WriterAddToKG("fake_id", runner, {})
    
    with pytest.raises(WriterConfigurationError):
        block.run()

def test_add_to_kg_wrong_type(monkeypatch, session, runner):
    monkeypatch.setattr("writer.ai.retrieve_graph", mock_retrieve_graph)
    monkeypatch.setattr("writer.ai.upload_file", mock_upload_file)

    session.state.my_files = "should be list"
    session.add_fake_component({
        "graphId": "abc123",
        "files": "{{my_files}}"
    })
    block = WriterAddToKG("fake_id", runner, {})
    
    with pytest.raises(WriterConfigurationError):
        block.run()