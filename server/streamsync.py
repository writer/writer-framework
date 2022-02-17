import uuid
import json


class StreamsyncState:


    def __init__(self):
        self.state = {}
        self.mutated = set()


    def __setitem__(self, key, value):
        self.state[key] = value
        self.mutated.add(key)


    def __getitem__(self, key):
        return self.state[key]
        

    def json_mutations(self):
        mutated_state = {x:self.state[x] for x in self.mutated}
        self.mutated = set()
        return json.dumps(mutated_state)


components = {}
initial_state = StreamsyncState()


def init_state(state_dict):
    for k, v in state_dict.items():
        initial_state[k] = v


def component(type, content=None, handlers=None):
    component_id = str(uuid.uuid4())

    components[component_id] = {
        "type": type,
        "content": content,
        "handlers": handlers
    }


def label(text, handlers=None):
    component("label", {"text": text}, handlers)


def heading(text, handlers=None):
    component("heading", {"text": text}, handlers)


def slider(value, handlers=None):
    component("slider", {"value": value}, handlers)


def button(text, handlers=None):
    component("button", {"text": text}, handlers)


def text(text, handlers=None):
    component("text", {"text": text}, handlers)
