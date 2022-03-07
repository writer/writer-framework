# Streamsync

Like Streamlit, but fast. A proof-of-concept framework built using JavaScript/Vue.js + Python/Flask + WebSockets.

By avoiding a rerun of the whole script, Streamsync can react more than 70 times faster. This is all achieved while maintaining a similar syntax. This repository is a companion to the following Medium article (no paywall), which explains how Streamsync was built, the tests conducted and the implications: .

Sample app:

```
import streamsync as ss

def increment(state, value=None): # Event handler which receives a copy of session state as an argument
    state["counter"] += 1

ss.init_state({"counter": 0}) # State initialisation

ss.text("The count is @counter.") # Template strings with references to state values
ss.button("Increment", handlers={"click": increment}) # Linking components to event handlers

with ss.when(lambda state: state["counter"] >= 10 and state["counter"] < 20): # Conditional rendering
    ss.text("Well done on reaching 10, here's a trophy: 🏆. Keep going!")

with ss.when(lambda state: state["counter"] >= 20):
    ss.text("You've earned a gold medal for reaching 20 🥇")
```

Please note that for the time being Streamsync isn't a viable, fully-fledged alternative to Streamlit, but rather a demonstration that a much faster alternative is possible. If there's some interest, I'll develop this into a viable alternative.


## Getting Started

The easiest way to test Streamsync is to clone the repository and use the Dockerfile provided.

This will run the app "user_script.py" and map Flask's port to 5010:

```
docker run -p 5010:5000 streamsync user_script
```

To create your own app, start by creating a .py file into the /server folder. Feel free to explore the examples user_script.py, user_script_2.py and user_script_3.py to get familiar with the syntax.

## Authors

* **Ramiro Medina**

## License

This project is licensed under the MIT License.