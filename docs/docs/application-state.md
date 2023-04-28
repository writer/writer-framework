# Application state

Streamsync assigns each session its own application state.

## Initialising state

The initial application state can be set by calling `ss.init_state()` and passing a `Dict` as argument. **All session states will kick off as a copy of the initial state**.

```py
import streamsync as ss

initial_state = ss.init_state({
    "counter": 0,
})

# Event handler
# It receives the session state as an argument and mutates it
def increment(state):
    state["counter"] += 1

```

In the example above, everyone starts with `counter` set to 0. But after users start interacting with the app and triggering event handlers, the value of `counter` will be different across sessions. Some users will trigger `increment` three times, making it 3. Some will trigger `increment` ten times, making it 10.

To reference `counter` from Builder, use `@{counter}`.

### Nested elements

Use dictionaries to set nested elements.

```py
ss.init_state({
    "counter": 0,
    "my_app": {
        "title": "Nested value"
    }
})
```

From Builder, you can reference the element above as `@{my_app.title}`.

### Backend-only elements

By default, all of the elements in the session state are sent to the frontend.

::: warning State elements are sent to the frontend by default
Even if they aren't actively being shown in the user interface, they're sent to the user's browser.
:::

Prefix a state element with `_` (underscore) to make them private (backend-only). This can be very useful in some scenarios.

- When synchronisation is not necessary. In some cases, we'll only need the data in the backend.
- When synchronisation is not possible, because the object can't be serialised / shown in the browser. For example, a database connection.
- When data is relevant to a specific session, but shouldn't be disclosed.

Since these elements stay in the backend and aren't synced, you cannot reference them from Builder.

## Non-standard types

The frontend cannot directly show objects such as a Pandas dataframe or a Matplotlib figure. Therefore, these objects need to be serialised before being sent to the browser. The following types of objects are automatically serialised.

### Matplotlib figures

They're converted to PNG data URLs, which can be shown using a standard _Image_ component.

```py
ss.init_state({
    "my_matplotlib_fig": fig,
})
```

The element can be used in an _Image_ component in Builder by setting the source to `@{my_matplotlib_fig}`. Alternatively, as data inside a _File Download_ component.

### Plotly graphs

They're converted to Plotly JS specifications, using JSON. They can be used in _Plotly Graph_ components.

### Altair charts

They're converted to Vega Lite specification, based on JSON. They can be used in _Vega Lite Chart_ components.

### Pandas dataframes

They're converted to JSON; they can be used in _Dataframe_ components.

## Files and binary data

In some components, Builder expects a data URL. The source of an _Image_ component can be a standard URL or a data URL.

**You can _pack_ files and binary data and they'll be converted to data URLs** before they reach the frontend. For this purpose, you can use `ss.pack_file()` and `ss.pack_bytes()` as shown below. The `mime_type` argument is optional for both functions —it helps the browser determine how to handle the data, by specifying the media type.

You can also directly assign bytes, but this won't allow you to specify the media type.

```py
import streamsync as ss

ss.init_state({
    # Use a string to reference a filesystem path
    "sales_spreadsheet": ss.pack_file("sales_spreadsheet.xlsx")

    # Use any file-like object with a .read() method
    "main_image": ss.pack_file(image_file, mime_type="image/jpeg"),

    # Work with raw bytes
    "my_bytes": ss.pack_bytes(b"\x31\x33\x33\x37", mime_type="text/plain"),

    # Send raw bytes, without specifying a MIME type
    "my_raw_bytes": b"\x31\x33\x33\x37"
})

```
