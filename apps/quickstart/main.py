import streamsync as ss
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_blobs
from streamsync.core import StreamsyncState

COLOR = {
    0: '#3c64fa',
    1: '#00eba8',
    2: '#5a677c',
    3: '#ff8866',
    4: '#d4b2f7',
    5: '#c3e6ff',
    6: '#045758',
    7: '#001435',
    8: '#ec3d10',
    9: '#38006a'
}

def line(x0, coef, intercept, c):
        return (-(x0 * coef[c, 0]) - intercept[c]) / coef[c, 1]

def update(state):
    cluster_std = state['cluster_std']
    multi_class = state['multi_class']
    maxsize = int(state['number_of_points'])
    groups = int(state['number_of_groups'])
    X, y = make_blobs(n_samples=maxsize, n_features=2, cluster_std=cluster_std,  centers=groups)

    clf = LogisticRegression(
        solver="sag", max_iter=1000, random_state=42, multi_class=multi_class
    ).fit(X, y)
    state["training"] = "training score : %.3f (%s)" % (clf.score(X, y), multi_class);
    coef = clf.coef_
    intercept = clf.intercept_

    data = []
    for i in range(groups):
        data.append(
            go.Scatter(
                x=X[y == i][:, 0], y=X[y==i][:, 1], mode='markers', name='Group '+str(i), hoverinfo='none',
                marker=dict(color=COLOR[i], symbol='circle', size=10)
            )
        )

    for i in range(1 if groups < 3 else groups):
        data.append(go.Scatter(
            x=[-20, 20], y=[line(-20, coef, intercept, i), line(20, coef, intercept, i)],
            mode='lines', line=dict(color=COLOR[i], width=2), name='Logistic Regression'
        ))

    layout = go.Layout(
        width=700,height=700,
        hovermode='closest', hoverdistance=1,
        xaxis=dict(title='Feature 1', range=[-20,20], fixedrange=True,
          constrain="domain", scaleanchor="y",scaleratio=1),
        yaxis=dict(title='Feature 2', range=[-20,20], fixedrange=True,
          constrain="domain"),
        paper_bgcolor='#EEEEEE',
        margin=dict(l=30, r=30, t=30, b=30),
    )

    fig = go.Figure(data=data, layout=layout)
    state['fig'] = fig


initial_state = ss.init_state({
    "multi_class_options": {"ovr": "One vs Rest", "multinomial": "Multinomial"},
    "multi_class": "ovr",
    "number_of_groups": 2,
    "number_of_points": 50,
    "cluster_std": 2,
})

update(initial_state)
