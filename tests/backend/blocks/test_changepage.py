import writer.core
from writer.blocks.changepage import ChangePage
from writer.core import WriterState


def test_change_page(session, runner):
    session.session_state = WriterState({}, [{"type": "test", "payload": "Just a test"}])
    component = session.add_fake_component({"pageKey": "secondaryPage"})
    writer.core.Config.is_mail_enabled_for_log = True
    block = ChangePage(component, runner, {})
    block.run()
    assert block.outcome == "success"
    latest_mail = session.session_state.mail[1]
    assert latest_mail.get("type") == "pageChange"
    assert latest_mail.get("payload") == "secondaryPage"
