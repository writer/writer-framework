import writer.ai
from writer.blocks.writercompletion import WriterCompletion


def test_complete(monkeypatch, session, runner, fake_client):
    def fake_complete(prompt, config):
        assert config.get("temperature") == 0.9
        assert config.get("model") == "buenos-aires-x-004"
        assert prompt == "What color is the sea?"
        return "Blue."

    monkeypatch.setattr("writer.ai.complete", fake_complete)
    component = session.add_fake_component(
        {"prompt": "What color is the sea?", "modelId": "buenos-aires-x-004", "temperature": "0.9"}
    )
    block = WriterCompletion(component, runner, {})
    block.run()
    assert block.result == "Blue."
    assert block.outcome == "success"


def test_complete_missing_text(monkeypatch, session, runner, fake_client):
    def fake_complete(prompt, config):
        assert config.get("temperature") == 0.9
        assert config.get("model") == "buenos-aires-x-004"
        assert not prompt
        return "Plants are usually green."

    monkeypatch.setattr("writer.ai.complete", fake_complete)
    component = session.add_fake_component(
        {"prompt": "", "modelId": "buenos-aires-x-004", "temperature": "0.9"}
    )
    block = WriterCompletion(component, runner, {})

    # Not expected to fail, just hallucinate

    block.run()
    assert block.result == "Plants are usually green."
    assert block.outcome == "success"
