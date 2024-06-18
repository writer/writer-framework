## What is Framework?

Writer Framework is an open-source framework for creating AI applications. Build user interfaces using a visual editor; write the backend code in Python.

Writer Framework is fast and flexible with a clean, easily-testable syntax. It provides separation of concerns between UI and business logic, enabling more complex applications.

## Highlights

### Reactive and state-driven

Writer Framework is **fully state-driven** and provides **separation of concerns** between user interface and business logic.

```py
import writer as wf

def handle_increment(state):
    state["counter"] += 1

wf.init_state({
    "counter": 0
})
```

The user interface is a template, which is defined visually. The template contains reactive references to state, e.g. `@{counter}`, and references to event handlers, e.g. when _Button_ is clicked, trigger `handle_increment`.

### Flexible

- Elements are highly customizable with no CSS required, allowing for shadows, button icons, background colors, etc.
- HTML elements with custom CSS can be included using the _HTML Element_ component. They can serve as containers for built-in components.

### Fast

- Event handling adds minimal overhead to your Python code (~1-2ms\*).
- Streaming (WebSockets) is used to synchronize frontend and backend states.
- The script only runs once.
- Non-blocking by default. Events are handled asynchronously in a thread pool running in a dedicated process.

\*End-to-end figure, including DOM mutation. Tested locally on a Macbook Air M2. [Measurement methodology](https://medium.com/@ramiromedina/measuring-time-elapsed-between-an-event-and-its-associated-dom-mutation-80431ad576e1).

### Developer-friendly

- It's all contained in a standard Python package, just one `pip install` away.
- User interfaces are saved as JSON, so they can be version controlled together with the rest of the application.
- Use your local code editor and get instant refreshes when you save your code. Alternatively, use the provided web-based editor.
- You edit the UI while your app is running. No hitting "Preview" and seeing something completely different to what you expected.

## Installation and Quickstart

Getting started with Writer Framework is easy. It works on Linux, Mac and Windows.

```sh
pip install writer
writer hello
```

- The first command will install Writer Framework using `pip`.
- The second command will create a demo application in the subfolder "hello" and start Writer Framework Builder, the framework's visual editor, which will be accessible via a local URL.

The following commands can be used to create, launch Writer Framework Builder and run an application.

```sh
writer create my_app
writer edit my_app
writer run my_app
```

## Documentation

Full documentation, including how to use Writer's AI module and deployment options, is available at [Writer](https://dev.writer.com/framework?utm_source=github&utm_medium=readme&utm_campaign=framework).

## About Writer

Writer is the full-stack generative AI platform for enterprises. Quickly and easily build and deploy generative AI apps with a suite of developer tools fully integrated with our platform of LLMs, graph-based RAG tools, AI guardrails, and more. Learn more at [writer.com](https://www.writer.com?utm_source=github&utm_medium=readme&utm_campaign=framework).

## License

This project is licensed under the Apache 2.0 License.
