def invoke_event_handler(event_handler, **kwargs):
    """
    Invokes an event handler in the same way that streamsync would.

    Middlewares are invoked.

    >>> import writer as wf
    >>> import writer.tests
    >>>
    >>> def handle_multiplication(state):
    >>>    state["r"] = state["a"] * state["b"]

    >>> s = wf.init_state({
    >>>    "a": 2,
    >>>    "b": 3,
    >>>    "r": None
    >>> })

    >>> writer.tests.invoke_event_handler(handle_multiplication, state=s)
    """
    event_handler(**kwargs)
