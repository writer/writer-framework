# State schema

Schema declaration on the [Application state](./application-state) allows Streamsync to handle complex serialization 
scenario and empower your IDE and toolchains to provide autocomplete and type checking.

## Schema declaration

```python
import streamsync as ss

class AppSchema(ss.StreamsyncState):
    counter: int

initial_state = ss.init_state({
    "counter": 0
}, schema=AppSchema)

# Event handler
# It receives the session state as an argument and mutates it
def increment(state: AppSchema):
    state.counter += 1
```

Access to an attribute by its key is always possible.

```python
def increment(state: AppSchema):
    state['counter'] += 1
```

Attributes missing from the schema remain accessible by their key.

```python
initial_state = ss.init_state({
    "counter": 0,
    "message": None
}, schema=AppSchema)

def increment(state: AppSchema):
    state['message'] = "Hello pigeon"
```

## Schema composition

Schema composition allows you to model a complex Application state.

```python
class MyappSchema(ss.State):
    title: str

class AppSchema(ss.StreamsyncState):
    my_app: MyappSchema
    counter: int

initial_state = ss.init_state({
    "counter": 0,
    "my_app": {
        "title": "Nested value"
    }
}, schema=AppSchema)
```

## Multi-level dictionary

Some components like Vega require specifying a graph in the form of a multi-level dictionary.

A schema allows you to specify to streamsync that an attribute which contains a dictionary 
must be treated as a dictionary and not as a group of state.

```python
class AppSchema(ss.StreamsyncState):
    vegas_graph: dict

# Without schema, this handler is execute only once
def handle_vega_graph(state: AppSchema):
    graph = state.vega_graph
    graph['data']['values'][0]['b'] += 1000
    state.vega_graph = graph
    
initial_state = ss.init_state({
    "vegas_graph": {
        "data": {
            "values": [
                {"a": "C", "b": 2}, {"a": "C", "b": 7}, {"a": "C", "b": 4},
                {"a": "D", "b": 1}, {"a": "D", "b": 2}, {"a": "D", "b": 6},
                {"a": "E", "b": 8}, {"a": "E", "b": 4}, {"a": "E", "b": 7}
            ]
        },
        "mark": "bar",
        "encoding": {
            "x": {"field": "a", "type": "nominal"},
            "y": {"aggregate": "average", "field": "b", "type": "quantitative"}
        }
    },
}, schema=AppSchema)
```

## Type checking

A schema allows you to check the integrity of your backend using the type system. 
The code below will raise an error with mypy.

```bash
$ mypy apps/myapp/main.py
apps/myapp/main.py:7: error: "AppSchema" has no attribute "countr"; maybe "counter"?  [attr-defined] 
```

Here is the code, can you spot the error ?

```python
import streamsync as ss

class AppSchema(ss.StreamsyncState):
    counter: int

def increment(state: AppSchema):
    state.countr += 1

initial_state = ss.init_state({
    "counter": 26,
}, schema=AppSchema)
```

