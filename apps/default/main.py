import writer as wf

# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://dev.writer.com/framework

# Shows in the log when the app starts
print("Starting dual driver app")


twoDriverData = {}
threeDriverData = {}

def sectionHandler(state, payload):
    print(payload)
    print("calling something for a response")
    if (payload['value'] == "2"):
        _set_driverSelected(state, "2")
    if (payload['value'] == "3"):
        _set_driverSelected(state, "3")


def _set_driverSelected(state, driverNumber):
    state["driverSelected"] = driverNumber
    state["thirdDriverVisible"] = (driverNumber == "3")
    
# Initialise the state

# "_my_private_element" won't be serialised or sent to the frontend,
# because it starts with an underscore

initial_state = wf.init_state({
    "my_app": {
        "title": "MY APP"
    },
    "_my_private_element": 1337,
    "message": None,
    "counter": 26,
    "servers": {
        "2": "two drivers",
        "3": "three drivers",
    },
    "thirdDriverVisible": False,
    "driverSelected": "",
})
