import streamsync as ss
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def replot(state, value):
    filtered_data = [x for x in generated_data if x < int(value)]
    fig, ax = plt.subplots()
    ax.plot(filtered_data)
    state["fig"] = fig


def increment(state, value=None):
    state["counter"] += 1

ss.init_state({ "filter_value": 0, "fig": None, "counter": 0 })
ss.text("The count is @counter.")
ss.button("Increment", handlers={"click": increment})

with ss.when(lambda state: state["counter"] >= 10 and state["counter"] < 20):
    ss.text("Well done on reaching 10, here's a trophy: 🏆. Keep going!")

with ss.when(lambda state: state["counter"] >= 20):
    ss.text("You've earned a gold medal for reaching 20 🥇")

mpl.use("Agg")
generated_data = np.random.randint(1, 1000, 300)
ss.slider("@filter_value", 0, 1000, handlers={"change": replot})
ss.pyplot("@fig")