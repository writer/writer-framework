# Modifying app UI through backend

Streamsync facilitates backend-initiated user interface modifications. These changes are made possible through **Code-Managed Components** (CMCs), distinct from *Builder-Managed Components* (BMCs). CMCs, unlike BMCs, are dynamically created via backend code, and cannot be edited (but still can be viewed) within the application builder. It's important to also note that CMCs do not persist in your application's `ui.json` file and exist only during the application runtime, supporting dynamic UI adjustments.

::: warning Experimental feature
This Streamsync feature is still evolving. You may encounter unexpected behavior. Your feedback is invaluable — please feel free to [share your experience and suggestions](https://github.com/streamsync-cloud/streamsync/discussions). 
:::

## UI manager

Streamsync provides two independent approaches for managing your application's UI: initializing a base UI and making session-specific updates.

### Initializing base UI

The `init_ui()` method sets up a UI manager to configure UI components at the application's startup. This creates a component set that is accessible across all sessions:

```python
import streamsync as ss

with ss.init_ui() as ui:
    with ui.Page(id="my-page"):
        ui.Header({"text": "Hello World!"})
```

### Making session-specific updates

For dynamic, session-specific UI updates, the `ui` parameter is used within handler functions. This approach allows for real-time modifications tailored to individual user sessions:

```python
def add_hello_world(ui, state):
    with ui.find("my-page"):
        ui.Text({"text": f"And welcome {state["username"]}!"})
```

## UI manager methods

### `find` method

You can use the `ui.find(component_id: str)` method to access existing components by ID:
```python
with ui.find("column-container"):
    with ui.Column():
        ...
```
If the component couldn't be found, the method raises a `RuntimeError`.

### Component methods

UI manager contains methods linked to each frontend component. In previous examples we've seen the `ui.Text` method used for creating [Text components](https://www.streamsync.cloud/component-list.html#text). 

This method accept `content: dict` as first argument, which enables you to modify the field properties of the component, through corresponding keys:
```python
ui.Text(
    {
        "text": "Hello World!",  # The text content of the component
        "useMarkdown": "no",  # Will not use Markdown
        "alignment": "left",  # Text is aligned to the left
        "primaryTextColor": "#000000",  # The text color is black
        "cssClasses": "my-text hello-world"  # Apply 'my-text' and 'hello-world' CSS classes
    }
)
```

In a similar way, every other component method also accepts `content` as its first argument:
```python
ui.VideoPlayer(
    {
        "src": "https://example.com/assets/mov/rick-roll-video.mov",
        "autoplay": "yes",
        "controls": "no",
        "muted": "no",
        "loop": "no",
    }
)
```

In addition to `content`, which is specific to the component type, you can also modify the base properties of the component itself, which are:
- **`id: str`**: A unique identifier used for accessing the component after it was created.
    *Providing an identifier that is already taken would result in `RuntimeWarning` and the existing component being overwritten with a newly created one.*
- **`position: int`**: Determines the display order of the component in relation to its siblings.
- **`parentId: str`**: Determines the parent [container](#container-components) for the component.
- **`visible: bool`**: Determines the visibility of the component.
- **`handlers: dict[str, callable]`**: Can be used to attach handlers to the events of the component:
    ```python
    def increment(state):
        state["counter"] += 1

    initial_state = ss.init_state({"counter": 0})

    ...
    
    ui.Button({"text": "My Counter: @{counter}"}, handlers={"ss-click": increment})
    # You have two options for adding a function to the `handlers` dictionary: 
    # directly pass the function itself, or use the function's name as a string. 
    # Both approaches yield the same outcome.
    ```
    *A component can be associated with multiple handlers through applicable events.*
- **`binding: dict[str, str]`**: Can be used to [bind](https://www.streamsync.cloud/builder-basics.html#binding) the component to a state element:
    ```python
    initial_state = ss.init_state({
        "header_text": "Default Text"
        "counter": 0
        })
    
    ...

    ui.TextInput(
        {"label": "Bound Text"}, 
        binding={"ss-change": "header_text"}
        )

    ui.SliderInput(
        {"minValue": 0, "maxValue": 300, "stepSize": 1}, 
        binding={"ss-number-change": "counter"}
        )
    ```
    *Note that, unlike handlers, a component can only be associated with a single variable through a bindable event. If the passed `binding` dictionary contains more than one pair of event name as key and variable name as value, it'll raise a `RuntimeError`.*

### Container components

Streamsync provides multiple layout components that can serve as *containers* for other components. 

You can use `with` keyword to define such layouts:
```python
with ui.Section({"title": "My Section"}):
    ui.Text({"text": 'Hello World!'}, id="hello-world")
```

It also allows for "chaining" multiple containers together, creating extensive and deeply-nested layout structures when needed:
```python
with ui.ColumnContainer(id="cmc-column-container"):
    with ui.Column(id="cmc-column-1"):
        with ui.Section({"title": "My Section 1"}):
            ui.Text({"text": 'Hello World!'}, id="hello-world-1")
    with ui.Column(id="cmc-column-2"):
        with ui.Section({"title": "My Section 2"}):
            ui.Text({"text": 'Hello World again!'}, id="hello-world-2")
```

::: warning Most components depend on being inside of a container
This means, for example, that Text components in code above cannot be created as "orphans", outside a Column or Section. Attempting to do so would raise an `UIError`.
:::

By default, components inside container's `with` are being *appended* to it:
```python
with ui.Column(id="cmc-column-1"):
    ui.Text({"text": 'Hello World!'}, id="hello-world-1")

...

with ui.find(id="cmc-column-1"): # retrieves the Column component created before
    # The following component is going to be appended to the retrieved Column
    ui.Text({"text": 'Hello World again!'}, id="hello-world-2")
```

This will result in a Column component having two children Text components.