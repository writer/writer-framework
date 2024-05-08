# Authentication

The StreamSync authentication module allows you to restrict access to your application.

Streamsync will be able to authenticate a user through an identity provider such as Google, Microsoft, Facebook, Github, Auth0, etc.

::: warning Authentication is done before accessing the application
Authentication is done before accessing the application. It is not possible to trigger authentication for certain pages exclusively.
:::

## Use OIDC provider

Authentication configuration is done in [the `server_setup.py` module](custom-server.md). The configuration depends on your identity provider. 
Here is an example configuration for Google.

<img src="./images/authentication_oidc_principle.png" style="width: 100%; margin: auto">

*server_setup.py*
```python
import os
import streamsync.serve
import streamsync.auth

oidc = streamsync.auth.Oidc(
    client_id="1xxxxxxxxx-qxxxxxxxxxxxxxxx.apps.googleusercontent.com",
    client_secret="GOxxxx-xxxxxxxxxxxxxxxxxxxxx",
    host_url=os.getenv('HOST_URL', "http://localhost:5000"),
    url_authorize="https://accounts.google.com/o/oauth2/auth",
    url_oauthtoken="https://oauth2.googleapis.com/token",
    url_userinfo='https://www.googleapis.com/oauth2/v1/userinfo?alt=json'
)

streamsync.serve.register_auth(oidc)
```
### Use pre-configured OIDC

StreamSync provides pre-configured OIDC providers. You can use them directly in your application.

|                                                                                    | Provider                                                                                | Function | Description                                                                                     |
|------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|----------|-------------------------------------------------------------------------------------------------|
| <img src="./images/auth_google_fill.png" style="width: 25px; min-width:25px" />    | Google  | `streamsync.auth.Google` | Allow your users to login with their Google Account                                             |
| <img src="./images/auth_microsoft_fill.png" style="width: 25px; min-width:25px" /> | Microsoft                                                                               | `streamsync.auth.Microsoft` | Allow your users to login with their Microsoft Account                                          |
| <img src="./images/auth_github_fill.png" style="width: 25px; min-width:25px" />    | Github                                                                                  | `streamsync.auth.Github` | Allow your users to login with their Github Account                                             |
| <img src="./images/auth_auth0_fill.png" style="width: 25px; min-width:25px" />     | Auth0                                                                                   | `streamsync.auth.Auth0` | Allow your users to login with different providers or with login password through Auth0 |


#### Google

You have to register your application into [Google Cloud Console](https://console.cloud.google.com/).

*server_setup.py*
```python
import os
import streamsync.serve
import streamsync.auth

oidc = streamsync.auth.Google(
	client_id="1xxxxxxxxx-qxxxxxxxxxxxxxxx.apps.googleusercontent.com",
	client_secret="GOxxxx-xxxxxxxxxxxxxxxxxxxxx",
	host_url=os.getenv('HOST_URL', "http://localhost:5000")
)

streamsync.serve.register_auth(oidc)
```

#### Auth0

You have to register your application into [Auth0](https://auth0.com/).

*server_setup.py*
```python
import os
import streamsync.serve
import streamsync.auth

oidc = streamsync.auth.Auth0(
	client_id="xxxxxxx",
	client_secret="xxxxxxxxxxxxx",
	domain="xxx-xxxxx.eu.auth0.com",
	host_url=os.getenv('HOST_URL', "http://localhost:5000")
)

streamsync.serve.register_auth(oidc)
```

[//]: # (### Callback to refuse access to the application)

[//]: # ()
[//]: # (### Callback to modify user information)


### Authentication workflow

<img src="./images/authentication_oidc.png" style="min-width: 25%; width: 35%; margin: auto">

## User information in event handler

When the `user_info` route is configured, user information will be accessible 
in the event handler through the `session` argument.

```python
def on_page_load(state, session):
    email = session['userinfo'].get('email', None)
    state['email'] = email
```

