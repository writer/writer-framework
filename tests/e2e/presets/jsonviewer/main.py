import writer as wf

initial_state = wf.init_state({
    "json": {
        "bool": True,
        "array": [1,2,3,4],
        "obj": {
            "key": "value",
            "nested": {
                "foo": "bar"
            }
        }
    },
})
