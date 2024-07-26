import contextlib
import copy

from writer import WriterState, core, core_ui
from writer.core import Config, SessionManager


@contextlib.contextmanager
def new_app_context():
    """
    Creates a new application context for testing, independent of the global state.

    This fixture avoids conflicts between tests that use the same global state.
    At the end of the context, the global state is restored to its original state.

    >>> with writer_fixtures.new_app_context():
    >>>     initial_state = wf.init_state({
    >>>            "counter": 0,
    >>>            "total": 0
    >>>     }, schema=MyState)
    """
    saved_context_vars = {}
    core_context_vars = ['initial_state', 'base_component_tree', 'session_manager']
    core_config_vars = copy.deepcopy(core.Config)

    for var in core_context_vars:
        saved_context_vars[var] = getattr(core, var)

    core.initial_state = WriterState()
    core.base_component_tree = core_ui.build_base_component_tree()
    core.session_manager = SessionManager()
    Config.mode = "run"
    Config.logger = None

    yield

    for var in core_context_vars:
        setattr(core, var, saved_context_vars[var])

    core.Config = core_config_vars
