import pytest
from writer.app_runner import AppRunner
from writer.ss_types import WriterEvent

from backend import test_app_dir
from backend.fixtures.app_runner_fixtures import init_app_session


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_app_runner")
async def test_middleware_should_apply_on_every_event_handler_invocation(setup_app_runner):
    # 08/06/2024 : the code that executes middleware is not yet implemented
    pytest.skip('this test is not implemented')
    # Given
    ar: AppRunner
    with setup_app_runner(test_app_dir, 'run', load=True) as ar:
        session_id = await init_app_session(ar)

        # When
        await ar.handle_event(session_id, WriterEvent(
            type='click',
            instancePath=[{'componentId': '5c0df6e8-4dd8-4485-a244-8e9e7f4b4675', 'instanceNumber': 0}],
            payload={})
        )

        # Then
        full_state = await ar.handle_state_content(session_id)
        assert full_state.payload.state['counter'] == 3
        assert full_state.payload.state['counter_middleware'] == 1
