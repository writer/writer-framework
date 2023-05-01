# Backend-initiated actions

Targeted, backend-initiated actions can be triggered from event handlers, using methods of `state`. Internally, this is achieved using Streamsync's `mail`, ephemeral state that is cleared when it reaches the intended user.

## Triggering a file download

The `file_download` method takes the `data` and `file_name` arguments. The first must contain raw bytes (a `bytes` object) or a packed file. As mentioned in the [Application State](application-state.html#files-and-binary-data) section of the guide, a packed file is obtained using the `ss.pack_file` or `ss.pack_bytes` methods.

```py
def handle_file_download(state):
    # Pack the file as a FileWrapper object
    data = ss.pack_file("assets/story.txt", "text/plain")
    file_name = "thestory.txt"
    state.file_download(data, file_name)
```

## Adding a notification

![Notifications](./images/backend-initiated-actions.notifications.png)

Streamsync adds notifications when a runtime error takes place. You can add your own notifications using the `add_notification` method, which takes the `type`, `title` and `message` arguments. `type` must be one of `error`, `warning`, `info`, `success`.

```py
def notify_of_things_that_happened(state):
    state.add_notification("error", "An Error", "Something bad happened.")
    state.add_notification("warning", "A Warning", "Be aware that something happened.")
    state.add_notification("info", "Some Info", "Something happened.")
    state.add_notification("success", "A Success", "Something good happened.")
```

## Opening a URL

Open a URL in a new tab using the `open_url` method, which takes the `url` argument.

```py
def handle_open_streamsync_website(state):
    state.open_url("https://streamsync.cloud")
```

The URL will be safely opened with `noopener` and `noreferrer` options.

::: warning Popup blockers
Given that the URL is opened asynchronously, popup blockers will likely block the new window —unless the user has opted in.
:::

## Changing the active page

The active page and route parameters can be changed using the methods `set_page` and `set_route_vars`. This is explained in more detail in [Page Routes](page-routes.html).
