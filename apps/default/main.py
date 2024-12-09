import writer as wf

# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://dev.writer.com/framework

# Shows in the log when the app starts
print("Hello world!")

# Its name starts with _, so this function won't be exposed
def _update_message(state):
    is_even = state["counter"] % 2 == 0
    message = ("+Even" if is_even else "-Odd")
    state["message"] = message

def decrement(state):
    state["counter"] -= 1
    _update_message(state)

def increment(state):
    state["counter"] += 1
    # Shows in the log when the event handler is run
    print("The counter has been incremented.")
    _update_message(state)
    
# Initialize the state

# "_my_private_element" won't be serialized or sent to the frontend,
# because it starts with an underscore

initial_state = wf.init_state({
    "my_app": {
        "title": "My app"
    },
    "_my_private_element": 1337,
    "message": None,
    "counter": 26,
})

_update_message(initial_state)