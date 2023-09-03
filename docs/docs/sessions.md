# Sessions

Sessions are designed for advanced use cases, being most relevant when Streamsync is deployed behind a proxy.

## Session information in event handlers

You can access the session's unique id, HTTP headers and cookies from event handlers via the `session` argument —similarly to how `state` and `payload` are accessed. The data made available here is captured in the HTTP request that initialised the session.

The `session` argument will contain a dictionary with the following keys: `id`, `cookies` and `headers`. Values for the last two are themselves dictionaries.

```py
# The following will output a dictionary
# with the session's id, cookies and headers.
def session_inspector(session):
    print(repr(session))
```

This enables you to adapt the logic of an event to a number of factors, such as the authenticated user's role, preferred language, etc.

## Session verifiers

You can use session verifiers to accept or deny a session based on headers or cookies, thus making sure that users without the right privileges don't get access to the initial state or components.

Session verifiers are functions decorated with `ss.session_verifier` and are run every time a user requests a session. A `True` value means that the session must be accepted, a `False` value means that the session must be rejected.

```py
import streamsync as ss

# Users without the header x-success will be denied the session

@ss.session_verifier
def check_headers(headers):
    if headers.get("x-success") is None:
        return False
    return True
```
