# Introduction

## What is Streamsync?

Streamsync is an open-source framework for creating data apps. Build user interfaces using a visual editor; write the backend code in Python.

![Streamsync Builder screenshot](/sc1.png)

It's an alternative to Plotly Dash, Streamlit and Gradio. Its focused on the creation of web applications for data analytics and machine learning.

It aims to be as simple as Streamlit, but faster, more flexible and with a cleaner, easily-testable syntax. It provides separation of concerns between UI and business logic, enabling more complex applications.

## Highlights

### Simple
Event handlers are defined as plain, easily-testable Python functions.

```py
def handle_increment(state):
    state["counter"] += 1

ss.init_state({
    "counter": 0
})
```

The event handler and state are linked to the UI using Streamsync Builder, the framework's visual editor.

![Counter Increment example](/introduction.counter.gif)

### Developer-friendly
- It's all contained in a standard Python package, just one `pip install` away.
- User interfaces are saved as JSON, so they can be version controlled together with the rest of the application.
- Use your local code editor and get instant refreshes when you save your code. Alternatively, use the provided web-based editor.
- You edit the UI while your app is running. No hitting "Preview" and seeing something completely different to what you expected.

### Fast
- Event handling adds minimal overhead to your Python code (~1-2ms*).
- Streaming (WebSockets) is used to synchronise frontend and backend states.
- The script only runs once.
- Non-blocking by default. Events are handled asynchronously in a thread pool running in a dedicated process.

*End-to-end figure, including DOM mutation. Tested locally on a Macbook Air M2. [Measurement methodology](https://medium.com/@ramiromedina/measuring-time-elapsed-between-an-event-and-its-associated-dom-mutation-80431ad576e1).

### Flexible
- Elements are highly customisable with no CSS required, allowing for shadows, button icons, background colours, etc.
- HTML elements with custom CSS can be included using the _HTML Element_ component. They can serve as containers for built-in components.
  

