import streamsync as ss


def increment(state, value=None):
    state["counter"] += 1
    state["evenodd"] = "even" if state["counter"] % 2 == 0 else "odd"

ss.init_state({
    "title": "Welcome to a Streamsync demo",
    "counter": 0,
    "evenodd": "even"
})

with ss.section("Counts"):
    ss.text("Streamsync supports session states, meaning that each user can have a personalised experience. The most straightforward example of this is a counter, for which the value is stored in the backend.")
    ss.button("Increment", handlers={"click": increment})
    ss.text("The count is @counter, which is @evenodd.")

with ss.when(lambda state: state["counter"] >= 10 and state["counter"] < 30):
    ss.text("Well done on reaching 10, here's a trophy: 🏆. Keep going!")

with ss.when(lambda state: state["counter"] >= 30):
    ss.text("You've earned a gold medal for reaching 30 🥇")
