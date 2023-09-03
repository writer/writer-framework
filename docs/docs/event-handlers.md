# Event handlers

Events originate in the frontend. For example, when a user clicks a _Button_ component. Using Builder, these events can be linked to event handlers.

## Plain Python functions

Event handlers are Python functions accessible from `main.py`. They can be defined in that same file or imported. No decorators or special syntax required.

```py
# This event handler will add an entry to the log
def handle_click()
    print("Hello")
```

To specify that a function isn't an event handler and should remain hidden to the frontend, prefix it with a `_` (underscore).

```py
# This function won't be visible in the frontend
# because its name starts with an underscore
def _reticulate(splines):
    r_splines = np.random.normal(size=(splines,100))
    return r_splines
```

## Mutating state

In most cases, event handlers will modify the application state. State can be accessed by including the `state` argument in the handler, which will provide you with a `StreamsyncState` object for the session that invoked the handler.

Elements of state can be reached using the square brackets syntax `state["my_element"]`. Accessing keys that don't exist will return `None`.

```py
def handle_click(state):
    state["counter"] += 1
```

The handler above receives the application state for the relevant session and mutates it. For example, if Bob's counter was 4, and he clicks on a _Button_ linked to `handle_click`, his new counter value will be 5. Other sessions remain unaffected.

## Mutation detection

When communicating with the frontend, Streamsync only sends state elements that have mutated.

To detect which elements have mutated, it relies on assignment (via operators such as `=`, `+=`, etc). This is because Python doesn't offer a performant, reliable mechanism to detect mutations. See the example below.

```py
def handle_click(state):
    state["my_df"].sample(frac=1, random_state=random.seed())

    # The self-assignment is necessary when mutating
    # an existing object directly on state

    state["my_df"] = state["my_df"]
```

The following, arguably cleaner, code, also works as it naturally relies on assignment.

```py
def handle_click(state):
    my_df = state["my_df"]
    my_df.sample(frac=1, random_state=random.seed())
    state["my_df"] = my_df # State assignmnet
```

::: warning Mutations are detected via assignment
Make sure you perform an assignment on the state element you're mutating, for the mutation to be detected.
:::

## Receiving a payload

Several events include additional data, known as the event's payload. The event handler can receive that data using the `payload` argument.

For example, the `ss-change` event in a _Text Input_ component is triggered every time the value changes. As a payload, it includes the new value.

```py
def handle_input_change(state, payload):
    state["value"] = payload
```

The content of the payload will vary depending on the event. For example, when a user takes a photo with a _Webcam Capture_, the picture they took is sent across as a PNG image.

```py
def handle_webcam_capture(payload):
	image_file = payload
	with open(f"picture.png", "wb") as file_handle:
		file_handle.write(image_file)
```

Handling different payloads across events can be challenging, especially since the shape of the payload may vary. To simplify this process, Builder provides stub code that can help you get started with writing an event handler. You can access it by clicking the icon located next to the event when configuring the component's settings. This feature can help you quickly understand the structure of the payload and start writing the appropriate code to handle it.

## Globals

You can use globals and module attributes, just as you would in a standard Python script. This is very convenient for storing a single copy of resource-intensive object.

```py
my_ai = CatIdentifierAI()

def evaluate(state, payload):
    result = my_ai.process(payload)
    state["is_a_cat"] = result
```

Take into account that globals apply to all users. If you need to store data that's only relevant to a particular user, use application state. 

## Standard output

The standard output of an app is captured and shown in the code editor's log. You can use the standard `print` function to output results.

```py
# Shown every time the app starts
print("Hello world")

def payload_inspector(state, payload):
    # Shown every time the event handler is executed
    print("Payload: " + repr(payload))
```

## Execution flow

Event handlers run in a thread pool and are non-blocking. Each event is processed independently from each other.

State mutations are sent to the frontend after the function has finished executing. The code below will accumulate all mutations and send to the frontend after the function returns.

```py
def handle_fast(state):
    state["text"] = "Hello"
    state["x"] += 3
    state["y"] += 2
```

However, for long-running tasks, Streamsync will periodically check state and provide partial updates to the user.

```py
def handle_slowly(state):
    state["message"] = "Loading..."
    import time
    time.sleep(5)
    state["message"] = "Completed"
```

The code above will set `message` to "Loading...", then to "Completed".  
