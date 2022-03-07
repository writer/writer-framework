import streamsync as ss

def increment(state, value=None):
    state["counter"] += 1

# If the "title" value is set, it's used as a title

ss.init_state({
    "counter": 0, "title": "App Name"
})

ss.heading("This is a heading")

with ss.section("This is a section title"):
    ss.text("The count is @counter.")
    ss.button("Increment", handlers={"click": increment})

    # Nested context managers for "section" and "when" components are allowed 

    with ss.when(lambda state: state["counter"] >= 10 and state["counter"] < 20):
        ss.text("Well done on reaching 10, here's a trophy: 🏆. Keep going!")

    with ss.when(lambda state: state["counter"] >= 20):
        ss.text("You've earned a gold medal for reaching 20 🥇")