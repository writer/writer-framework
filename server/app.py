import flask
from flask_cors import cross_origin
import flask_sock
import json
import copy

import handlers


app = flask.Flask(__name__, static_url_path="/static")
sock = flask_sock.Sock(app)


# Pack the initial state and components

@app.route("/api/init")
@cross_origin()
def init():
    response_payload = {
        "state": handlers.ss.initial_state.state,
        "components": handlers.ss.components
    } 
    response = json.dumps(response_payload, default=lambda x: True) # Replace handler functions for True
    
    return response


# Listen to events, call the handlers, respond with mutations

@sock.route('/api/echo')
def echo(sock):
    session_state = copy.deepcopy(handlers.ss.initial_state)
    while True:
        data = json.loads(sock.receive())
        type = data["type"]
        
        if type != "keep_alive":
            target_id = data["targetId"]
            value = data["value"]
            handlers.ss.components[target_id]["handlers"][type](session_state, value)
        else:
            handlers.keep_alive(session_state)
        
        sock.send(session_state.json_mutations())


@app.route("/<path:path>")
def send_static(path):
    directory = app.root_path + "/static"
    return flask.send_from_directory(directory=directory, path=path)


if __name__ == "__main__":
    app.run(host='0.0.0.0')