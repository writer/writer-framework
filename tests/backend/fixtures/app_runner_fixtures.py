from typing import Optional

from writer.app_runner import AppRunner
from writer.ss_types import InitSessionRequestPayload

FIXED_SESSION_ID = "0000000000000000000000000000000000000000000000000000000000000000"

async def init_app_session(app_runner: AppRunner,
                           session_id: str = None,
                           cookies: Optional[dict] = None,
                           headers: Optional[dict] = None) -> str:
    """
    Creates a session in writer framework for automatic testing

    Creates a session with a random ID.

    >>> with setup_app_runner(test_app_dir, 'run') as ar:
    >>>     # When
    >>>     ar.load()
    >>>     session_id = await init_app_session(ar)

    Creates a session with a fixed identifier.

    >>>     session_id = await init_app_session(ar, session_id=FIXED_SESSION_ID)
    """
    if cookies is None:
        cookies = {}
    if headers is None:
        headers = {}

    init_session_payload = InitSessionRequestPayload(cookies=cookies, headers=headers, proposedSessionId=session_id)
    result = await app_runner.init_session(init_session_payload)

    return result.payload.model_dump().get("sessionId")
