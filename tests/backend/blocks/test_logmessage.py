import pytest
import writer.core
from writer.blocks.logmessage import LogMessage


def test_log_message(session, runner):
    session.globals = {
        "animal": "rat",
    }
    session.add_fake_component({
        "message": "The quick brown fox is under the table."
    })
    writer.core.Config.is_mail_enabled_for_log = True
    block = LogMessage("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    latest_mail = session.mail.mail[0]
    assert latest_mail.get("type") == "logEntry"
    assert latest_mail.get("payload").get("type") == "info"
    assert latest_mail.get("payload").get("message") == "The quick brown fox is under the table."


def test_log_message_with_template(session, runner):
    session.state._state_data = {
        "animal": "rat",
    }
    session.add_fake_component({
        "message": "The quick brown {{animal}} is under the {{object}}."
    })
    writer.core.Config.is_mail_enabled_for_log = True
    block = LogMessage("fake_id", runner, {
        "object": "tent"
    })
    block.run()
    assert block.outcome == "success"
    latest_mail = session.mail.mail[0]
    assert latest_mail.get("type") == "logEntry"
    assert latest_mail.get("payload").get("type") == "info"
    assert latest_mail.get("payload").get("message") == "The quick brown rat is under the tent."


def test_log_error_message(session, runner):
    session.state._state_data = {
        "animal": "squirrel",
    }
    session.add_fake_component({
        "type": "error",
        "message": "The quick brown {{animal}} has escaped."
    })
    writer.core.Config.is_mail_enabled_for_log = True
    block = LogMessage("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    latest_mail = session.mail.mail[0]
    assert latest_mail.get("type") == "logEntry"
    assert latest_mail.get("payload").get("type") == "error"
    assert latest_mail.get("payload").get("message") == "The quick brown squirrel has escaped."


def test_empty_message(session, runner):
    session.state._state_data = {
        "animal": None,
    }
    session.add_fake_component({
        "type": "error",
        "message": "{{animals}}"
    })
    writer.core.Config.is_mail_enabled_for_log = True
    block = LogMessage("fake_id", runner, {})
    with pytest.raises(ValueError):
        block.run()
    assert block.outcome == "error"