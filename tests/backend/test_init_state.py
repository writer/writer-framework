import contextlib
from typing import Optional

import writer.core
from writer.core import State, WriterState


@contextlib.contextmanager
def use_dedicated_writer_initial_state():
    """

    Returns
    -------

    """
    previous_state = writer.core.initial_state
    yield
    writer.core.initial_state = previous_state

def test_init_state_should_build_simple_writer_state_without_schema():
    """
    Tests that `writer.init_state` without schema returns a WriterState object.
    """
    with use_dedicated_writer_initial_state():
        # When
        state = writer.init_state({})

        # Then
        assert isinstance(state, WriterState)


def test_init_state_with_schema_should_inherits_writer_state():
    """
    Tests that `writer.init_state` with schema returns a WriterState object.
    """
    class SimpleSchema(WriterState):
        value: int
        message: Optional[str]

    with use_dedicated_writer_initial_state():
        # When
        state = writer.init_state({'value': 1, 'message': None, 'hello': 2}, schema=SimpleSchema)

        # Then
        assert isinstance(state, SimpleSchema)
        assert state.value == 1
        assert state.message is None
        assert state['hello'] == 2


def test_init_state_should_build_a_state_with_a_schema_that_contains_a_substate():
    """
    Tests that `writer.init_state` constructs an instance with schema that contains a substate.
    """
    class AppState(State):
        title: str

    class ComplexSchema(WriterState):
        app: AppState
        value: int
        message: Optional[str]

    with use_dedicated_writer_initial_state():
        # When
        state = writer.init_state({'app': {'title': 'hello'}, 'value': 1, 'message': None, 'hello': 2}, schema=ComplexSchema)

        # Then
        assert isinstance(state, ComplexSchema)
        assert isinstance(state.app, AppState)
        assert state.app.title == 'hello'
        assert state['hello'] == 2

        # A State Proxy instance is directly linked to the State Proxy instance of a child state
        assert state._state_proxy.state['app'] is state.app._state_proxy





def test_init_state_with_state_accept_raw_values_that_deviates_from_the_expected_type():
    """
    Tests that `writer.init_state` with schema accepts in raw state values that deviate from the expected type.
    """
    class AppState(State):
        year: int

    class ComplexSchema(WriterState):
        app: AppState
        value: int
        message: Optional[str]

    with use_dedicated_writer_initial_state():
        # When
        state = writer.init_state({'app': {'year': 'hello'}, 'value': 1, 'message': None, 'hello': 2}, schema=ComplexSchema)

        # Then
        assert isinstance(state, ComplexSchema)
        assert state.value == 1
        assert state.app.year == 'hello'
        assert state.message is None
        assert state['hello'] == 2