import streamsync as ss


def mouseover(state, value=None):
    state["message"] = "You're mouseovering me."


def mouseout(state, value=None):
    state["message"] = "You're not mouseovering me"


ss.init_state({"message": "You're not mouseovering me", "title": "Streamsync demo"})
with ss.section():
    ss.heading("@message", handlers={"mouseover": mouseover, "mouseout": mouseout})