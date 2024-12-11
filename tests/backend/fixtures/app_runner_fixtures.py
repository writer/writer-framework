import contextlib
from typing import Optional

from writer.app_runner import AppRunner
from writer.core import session_manager, use_request_context
from writer.ss_types import AppProcessServerRequest, InitSessionRequestPayload

FIXED_SESSION_ID = "0000000000000000000000000000000000000000000000000000000000000000" # Compliant session number

async def init_app_session(app_runner: AppRunner,
                           session_id: str = None,
                           cookies: Optional[dict] = None,
                           headers: Optional[dict] = None) -> str:
    """
    Fixture to initialize a session and be able to use it in tests.

    If the `session_id` is missing from the parameters, the fixture creates a session with a random ID.

    >>> with setup_app_runner(test_app_dir, 'run') as ar:
    >>>     # When
    >>>     ar.load()
    >>>     session_id = await init_app_session(ar)

    If the `session_id` is missing from the parameters, the fixture creates a session for this identifier.

    >>>     session_id = await init_app_session(ar, session_id=FIXED_SESSION_ID)
    """
    if cookies is None:
        cookies = {}
    if headers is None:
        headers = {}

    init_session_payload = InitSessionRequestPayload(cookies=cookies, headers=headers, proposedSessionId=session_id)
    result = await app_runner.init_session(init_session_payload)

    return result.payload.model_dump().get("sessionId")


@contextlib.contextmanager
def within_message_request(session_id=FIXED_SESSION_ID, request: AppProcessServerRequest=None):
    """
    This fixture starts a session and emulates the context of an event message.

    >>>  with within_message_request():
    >>>    _session = core.get_session()
    >>>    _session.local_storage['key'] = "value"

    :param session_id: the session identifier
    :param request: the request to create
    """
    if request is None:
        request = AppProcessServerRequest(type="event")

    session_manager.get_new_session(proposed_session_id=session_id)
    with use_request_context(session_id=session_id, request=request):
        yield
