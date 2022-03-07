import flask
import flask_sock
import json
import copy
import importlib
import sys


user_script = importlib.import_module(sys.argv[1]) # Dynamically import user script
app = flask.Flask(__name__, static_url_path="/static")
sock = flask_sock.Sock(app)


# Pack the initial state and components

@app.route("/api/init")
def init():
    initial_state = user_script.ss.initial_state.state
    active_components = user_script.ss.get_active_components(initial_state)
    response_payload = {
        "state": initial_state,
        "components": active_components
    } 
    response = json.dumps(response_payload, default=lambda x: True)
    
    return response


# Listen to events. Keep the WebSockets stream open and waiting for forwarded events from the frontend.
# Call the event handlers. These will likely modify session state.
# Respond with state mutations and active components.

@sock.route("/api/echo")
def echo(sock):

    # Each session gets its own state, initialised with the contents of the initial state.

    session_state = copy.deepcopy(user_script.ss.initial_state)
    while True:
        data = json.loads(sock.receive())
        type = data["type"]
        target_id = data["targetId"]
        value = data["value"]

        # Get active components. That is, components that don't depend on a conditioner (conditional rendering function)
        # or components for which their conditioner returns True.

        session_components = user_script.ss.get_active_components(session_state)

        # Trigger handler (component needs to be active in the session)
        
        session_components[target_id]["handlers"][type](session_state, value)

        # Reobtaining session components to account for state changes that may have caused components to become active/inactive

        session_components = user_script.ss.get_active_components(session_state)

        sock.send(json.dumps({
            "mutations": session_state.mutations(),
            "components": session_components
        }, default=lambda x: True))


# Serve static files

@app.route("/<path:path>")
def send_static(path):
    directory = app.root_path + "/static"
    return flask.send_from_directory(directory=directory, path=path)


# Start Flask

if __name__ == "__main__":
    app.run(host='0.0.0.0')