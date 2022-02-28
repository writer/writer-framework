import flask
import flask_sock
import json
import copy

import handlers


app = flask.Flask(__name__, static_url_path="/static")
sock = flask_sock.Sock(app)


# Pack the initial state and components

@app.route("/api/init")
def init():
    initial_state = handlers.ss.initial_state.state
    active_components = handlers.ss.get_active_components(initial_state)
    response_payload = {
        "state": initial_state,
        "components": active_components
    } 
    response = json.dumps(response_payload, default=lambda x: True) # Replace handler functions for True
    
    return response


# Listen to events, call the handlers, respond with mutations

@sock.route("/api/echo")
def echo(sock):
    session_state = copy.deepcopy(handlers.ss.initial_state)
    while True:
        data = json.loads(sock.receive())
        type = data["type"]
        target_id = data["targetId"]
        value = data["value"]
        session_components = handlers.ss.get_active_components(session_state)

        # Trigger handler (component needs to be active in the session)
        session_components[target_id]["handlers"][type](session_state, value)

        # Reobtaining session components to account for state changes that may have caused components to become active/inactive
        session_components = handlers.ss.get_active_components(session_state)

        sock.send(json.dumps({
            "mutations": session_state.mutations(),
            "components": session_components
        }, default=lambda x: True))


@app.route("/<path:path>")
def send_static(path):
    directory = app.root_path + "/static"
    return flask.send_from_directory(directory=directory, path=path)


if __name__ == "__main__":
    app.run(host='0.0.0.0')