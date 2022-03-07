# Streamsync

Like Streamlit, but fast. A proof-of-concept framework built using JavaScript/Vue + Python/Flask + WebSockets.

By avoiding a rerun of the whole script, Streamsync can be more than 70 times faster. This Medium article (no paywall) explains how Streamsync was built, the tests conducted and the implications: .

Please note that for the time being Streamsync isn't a viable, fully-fledged alternative to Streamlit, but rather a demonstration that a much faster alternative is possible. If there's some interest, I'll develop this into a viable alternative.


## Getting Started

The easiest way to test Streamsync is to clone the repository and use the Dockerfile provided.

This will run the app "user_script.py" and map Flask's port to 5010:

```
docker run -p 5010:5000 streamsync user_script
```

To create your own app, start by creating a .py file into the /server folder.

Feel free to explore the examples user_script.py and user_script_2.py to get familiar with the syntax.

## Authors

* **Ramiro Medina**

## License

This project is licensed under the MIT License