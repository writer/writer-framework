## What is Streamsync?

Streamsync is an open-source framework for creating data apps. Build user interfaces using a visual editor; write the backend code in Python. 

![Streamsync Builder screenshot](https://raw.githubusercontent.com/streamsync-cloud/streamsync/master/docs/docs/public/sc1.png "Streamsync Builder screenshot")

- [Live demo](https://hello.streamsync.cloud/) of an app. [Source code](https://github.com/streamsync-cloud/streamsync/blob/master/apps/hello/main.py).
- [1 minute introduction video](https://youtu.be/XBAPBy_zf8s) on YouTube

It's an alternative to Plotly Dash, Streamlit and Gradio. Its focused on the creation of web applications for data analytics and machine learning.

It aims to be as simple as Streamlit, but faster, more flexible and with a cleaner, easily-testable syntax. It provides separation of concerns between UI and business logic, enabling more complex applications.

## Highlights

### Reactive and state-driven

Streamsync is **fully state-driven** and provides **separation of concerns** between user interface and business logic. 

```py
import streamsync as ss

def handle_increment(state):
    state["counter"] += 1

ss.init_state({
    "counter": 0
})
```

The user interface is a template, which is defined visually. The template contains reactive references to state, e.g. `@{counter}`, and references to event handlers, e.g. when _Button_ is clicked, trigger `handle_increment`.

### Flexible
- Elements are highly customisable with no CSS required, allowing for shadows, button icons, background colours, etc.
- HTML elements with custom CSS can be included using the _HTML Element_ component. They can serve as containers for built-in components.

### Fast
- Event handling adds minimal overhead to your Python code (~1-2ms*).
- Streaming (WebSockets) is used to synchronise frontend and backend states.
- The script only runs once.
- Non-blocking by default. Events are handled asynchronously in a thread pool running in a dedicated process.

*End-to-end figure, including DOM mutation. Tested locally on a Macbook Air M2. [Measurement methodology](https://medium.com/@ramiromedina/measuring-time-elapsed-between-an-event-and-its-associated-dom-mutation-80431ad576e1).

### Developer-friendly
- It's all contained in a standard Python package, just one `pip install` away.
- User interfaces are saved as JSON, so they can be version controlled together with the rest of the application.
- Use your local code editor and get instant refreshes when you save your code. Alternatively, use the provided web-based editor.
- You edit the UI while your app is running. No hitting "Preview" and seeing something completely different to what you expected.

## Installation and Quickstart

Getting started with Streamsync is easy. It works on Linux, Mac and Windows.

```sh
pip install "streamsync[ds]"
streamsync hello
```

- The first command will install Streamsync using `pip` and include the optional data science dependencies.
- The second command will create a demo application in the subfolder "hello" and start Streamsync Builder, the framework's visual editor, which will be accessible via a local URL.

The following commands can be used to create, launch Streamsync Builder and run an application.

```sh
streamsync create my_app
streamsync edit my_app
streamsync run my_app
```

## Documentation

Documentation is available online at [streamsync.cloud](https://streamsync.cloud).

## License

This project is licensed under the Apache 2.0 License.
