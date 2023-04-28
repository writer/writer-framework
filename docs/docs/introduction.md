# Introduction

## What is Streamsync?

Streamsync is an open-source framework for creating data apps. Build user interfaces using a visual editor; write the backend code in Python.

![Streamsync Builder screenshot](/sc1.png)

### It's fast.

- Streamsync enables significantly lower response times, when compared to Streamlit.
- It only runs the user script once.
- It uses WebSockets to keep frontend and backend states in sync.

### It's neat.

- Streamsync uses state-driven, reactive user interfaces. A data app's user interface is strictly separated from its logic.
- It uses a consistent yet customisable UI design system.
- No caching needed; the script runs once and things remain in memory.
- Predictable flow of execution. Event handlers are defined in the Python code and invoked from the user interface.

It's all contained in a standard Python package, just one `pip install` away.
