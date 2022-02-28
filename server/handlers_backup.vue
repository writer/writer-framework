import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import streamsync as ss

mpl.use("Agg")


def clack(state, value=None):
    state["overtest"] = "You are mouseovering me"


def cleck(state, value=None):
    state["overtest"] = "You are not mouseovering me"


def increment(state, value=None):
    state["counter"] += 1


def replot(state, value):
    generated_data = np.random.randint(1, 100, 3000)

    state["filter_value"] = int(value)
    state["filter_label"] = f"Filtering out values of more than { int(value) }"

    filtered_data = [x for x in generated_data if x < state["filter_value"]]
    fig, ax = plt.subplots()
    ax.plot(filtered_data)
    
    iobytes = io.BytesIO()
    plt.savefig(iobytes, format="png")
    iobytes.seek(0)
    base64_str = base64.b64encode(iobytes.read()).decode("latin-1")
    dataurl = "data:image/png;base64," + base64_str
    plt.close()
    state["plot"] = dataurl


ss.init_state({
    "filter_value": None,
    "plot": None,
    "time_updated": None,
    "filter_label": None,
    "overtest": "You are not mouseovering me",
    "counter": 0
})

ss.heading("Welcome to a Streamsync demo")
ss.label("@filter_label")
ss.slider("@filter_value", handlers={"change": replot})
ss.label("@overtest", handlers={"mouseover": clack, "mouseout": cleck})

with ss.when("@show_trophy"):
    ss.text("perro")

with ss.section("Counts"):
    ss.button("Increment", handlers={"click": increment})
    ss.text("The count is @counter, again @counter")
    ss.text("My email is ramiro.a.medina\@gmail.com")

#ss.image(plot)