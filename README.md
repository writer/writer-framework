## What is Streamsync?

Streamsync is an open-source framework for creating data apps. Build user interfaces using a visual editor; write the backend code in Python.

![Streamsync Builder screenshot](docs/docs/public/sc1.png "Streamsync Builder screenshot")

### It's fast.

- Streamsync enables significantly lower response times, when compared to Streamlit.
- It only runs the user script once.
- It uses WebSockets to keep frontend and backend states in sync.

### It's neat.

- Streamsync uses state-driven, reactive user interfaces. A data app's user interface is strictly separated from its logic.
- It uses a consistent yet customisable UI design system.
- No caching needed; the script runs once and things remain in memory. You can use globals and module attributes to store app-wide data.
- Predictable flow of execution. Event handlers are plain, easily testable Python functions. No re-runs, no strange decorators.

## Installation and Quickstart

Getting started with Streamsync is easy. It works on Linux, Mac and Windows.

```sh
pip install streamsync
streamsync hello
```

- The first command will install Streamsync using `pip`.
- The second command will create a demo application in the subfolder "hello" and start Streamsync Builder, the framework's visual editor, which will be accessible via a local URL.

We recommend using a virtual environment.

## Documentation

Documentation is available online at [streamsync.cloud](https://streamsync.cloud).

## License

This project is licensed under the Apache 2.0 License.
