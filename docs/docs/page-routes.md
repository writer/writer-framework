# Page routes

Streamsync apps can have multiple pages, with parametrised routes. Pages can be switched from the frontend or the backend.

## Basic navigation

To enable navigation between _Page_ components, they must have a key assigned. This can be set up from the component's settings. Once a key is set up, the page will be accessible at `/#my_page_key`.

### Frontend-triggered page changes

For basic page changes, assign a "Go to page" action to an event handler. For example, if you want to change to page `my_page_key` when a _Button_ is clicked, go to the button's settings and under the `click` event select `Go to page "my_page_key"`.

### Backend-triggered page changes

Trigger a page change from the backend using the `set_page` method of state.

```py
# This event handler sends the user to a different page
# depending on time of the day
def handle_click(state):
    from datetime import datetime

    now = datetime.now()
    if now.hour >= 18:
        state.set_page("fun_work_page")
    else:
        state.set_page("work_work_page")
```

## Routes with parameters

You may want to share a URL that links directly to a specific resource within your app. For example, to a specific location or product.

You can do so by specifying parameters in the URL, known as route vars. Streamsync URLs contain the page key, followed by the route vars and their values. For example, `/#detailPage/product_id=32&country=AR`.

### Adding vars to the URL from the backend

You can set up variables that are displayed in the URL by passing a dictionary to the `set_route_vars` state method. Use `None` to clear specific keys.

```py
# The following code will set the value of product_id
# to the value of the "product" state element
def change_route_vars(state):
    state.set_route_vars({
        "product_id": state["product"]
    })
```

### Retrieving the values

Streamsync uses the hash portion of the URL to store page and variable data, so even when switching pages or changing variables, the page doesn't reload. To monitor changes to the active URL, set up an event handler for `ss-hashchange` in the _Root_ component.

```py
# The following event handler reads the product_id route var,
# then assigns its value to the "product" state element.
def handle_hash_change(state, payload):
    route_vars = payload.get("route_vars")
    if not route_vars:
        return
    state["product"] = route_vars.get("product_id")
```
