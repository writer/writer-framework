import writer as wf

initial_state = wf.init_state({
    "types": {
        "none": None,
        "string": "Hello, World!",
        "integer": 42,
        "float": 3.14,
    },
    "counter": 26,
    "list": ["A", "B", "C"],
    "dict": {"a": 1, "b": 2},
    "nested": {
        "a": 1,
        "b": 2,
        "c": {
            "d": 3,
            "e": 4
        }
    },

    "nested_list": [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ],
    "code": ""
})

def execute_test(state):
    exec(state['code'])

