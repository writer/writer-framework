import streamsync as ss
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def replot(state, value):
    filtered_data = [x for x in generated_data if x < int(value)]
    fig, ax = plt.subplots()
    ax.plot(filtered_data)
    state["fig"] = fig


mpl.use("Agg")
generated_data = np.random.randint(1, 1000, 300)
ss.init_state({ "filter_value": 0, "fig": None })
ss.slider("@filter_value", 0, 1000, handlers={"change": replot})
ss.pyplot("@fig")