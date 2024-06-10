import pytest

import writer.tests
from backend import test_app_dir
from backend.test_app_runner import setup_app_runner


@pytest.mark.usefixtures("setup_app_runner")
def test_middleware_should_apply_on_every_event_handler_invocation(setup_app_runner):
    # 08/06/2024 : the code that executes middleware is not yet implemented
    # pytest.skip('this test is not implemented')
    # Given
    with setup_app_process():
        import writer as wf
        @wf.middleware()
        def my_middleware(state):
            state['counter'] += 1
            yield

        def handle_multiplication(state):
            state["r"] = state["a"] * state["b"]

        s = wf.init_state({
            "counter": 0,
            "a": 2,
            "b": 3,
            "r": None
        })

        # When
        writer.tests.invoke_event_handler(handle_multiplication, state=s)

        # Then
        assert s["counter"] == 1
