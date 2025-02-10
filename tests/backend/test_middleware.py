from pathlib import Path
import pytest
from writer.app_runner import AppRunner
from writer.ss_types import WriterEvent

from backend import test_app_dir
from backend.fixtures.app_runner_fixtures import init_app_session

test_app_dir = Path(__file__).resolve().parent / "basic_test_app"

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_app_runner")
async def test_middleware_should_apply_on_every_event_handler_invocation(setup_app_runner):
    """
    Tests that a middleware executes before an event
    """
    # Given
    ar: AppRunner
    with setup_app_runner(test_app_dir, 'run', load=True) as ar:
        session_id = await init_app_session(ar)

        # When
        res = await ar.handle_event(session_id, WriterEvent(
            type='click',
            instancePath=[{'componentId': '5c0df6e8-4dd8-4485-a244-8e9e7f4b4675', 'instanceNumber': 0}],
            payload={})
        )
        res.payload.mutations['+counter_middleware'] = 1

        # Then
        full_state = await ar.handle_state_content(session_id)
        assert full_state.payload.state['counter'] == 3
        assert full_state.payload.state['counter_middleware'] == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_app_runner")
async def test_middleware_should_apply_on_multi_event_handler_invocation(setup_app_runner):
    """
    Tests that a middleware executes twice after 2 different events
    """
    # Given
    ar: AppRunner
    with setup_app_runner(test_app_dir, 'run', load=True) as ar:
        session_id = await init_app_session(ar)

        # When
        res = await ar.handle_event(session_id, WriterEvent(
            type='click',
            instancePath=[{'componentId': '5c0df6e8-4dd8-4485-a244-8e9e7f4b4675', 'instanceNumber': 0}],
            payload={})
        )
        res.payload.mutations['+counter_middleware'] = 1

        res = await ar.handle_event(session_id, WriterEvent(
            type='wf-option-change',
            instancePath=[{'componentId': '2e46c38b-6405-42ad-ad9c-d237a53a7d30', 'instanceNumber': 0}],
            payload='ar')
        )
        res.payload.mutations['+counter_middleware'] = 2

        # Then
        full_state = await ar.handle_state_content(session_id)
        assert full_state.payload.state['counter_middleware'] == 2


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_app_runner")
async def test_middleware_should_apply_after_event_handler_invocation(setup_app_runner):
    """
    Test that a middleware executes after an event
    """
    # Given
    ar: AppRunner
    with setup_app_runner(test_app_dir, 'run', load=True) as ar:
        session_id = await init_app_session(ar)

        # When
        res = await ar.handle_event(session_id, WriterEvent(
            type='click',
            instancePath=[{'componentId': '5c0df6e8-4dd8-4485-a244-8e9e7f4b4675', 'instanceNumber': 0}],
            payload={})
        )
        res.payload.mutations['+counter_post_middleware'] = 1

        # Then
        full_state = await ar.handle_state_content(session_id)
        assert full_state.payload.state['counter'] == 3
        assert full_state.payload.state['counter_post_middleware'] == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_app_runner")
async def test_middleware_should_apply_on_middleware_without_yield(setup_app_runner):
    """
    Test that a middleware executes after an event
    """
    # Given
    ar: AppRunner
    with setup_app_runner(test_app_dir, 'run', load=True) as ar:
        session_id = await init_app_session(ar)

        # When
        res = await ar.handle_event(session_id, WriterEvent(
            type='click',
            instancePath=[{'componentId': '5c0df6e8-4dd8-4485-a244-8e9e7f4b4675', 'instanceNumber': 0}],
            payload={})
        )
        res.payload.mutations['+counter_middleware_without_yield'] = 1

        # Then
        full_state = await ar.handle_state_content(session_id)
        assert full_state.payload.state['counter_middleware_without_yield'] == 1
