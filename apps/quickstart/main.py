import plotly.graph_objects as go
import writer as wf
from sklearn.datasets import make_blobs
from sklearn.linear_model import LogisticRegression

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

def _line(x0, coef, intercept, c):
        return (-(x0 * coef[c, 0]) - intercept[c]) / coef[c, 1]

def update(state):
    cluster_std = state['cluster_std']
    multi_class = state['multi_class']
    number_of_points = int(state['number_of_points'])
    number_of_groups = int(state['number_of_groups'])
    X, y = make_blobs(
        n_samples=number_of_points,
        n_features=2,
        cluster_std=cluster_std,
        centers=number_of_groups
    )

    clf = LogisticRegression(
        solver="sag",
        max_iter=1000,
        random_state=42,
        multi_class=multi_class
    ).fit(X, y)

    coef = clf.coef_
    intercept = clf.intercept_
    score = clf.score(X, y)

    state["message"] = "training score : %.3f (%s)" % (score, multi_class)

    data = []
    for i in range(number_of_groups):
        data.append(
            go.Scatter(
                x=X[y == i][:, 0],
                y=X[y==i][:, 1],
                mode='markers',
                name='Group '+str(i),
                hoverinfo='none',
                marker={
                    'color': COLOR[i],
                    'symbol': 'circle',
                    'size': 10
                }
            )
        )

    for i in range(1 if number_of_groups < 3 else number_of_groups):
        data.append(go.Scatter(
            x=[-20, 20],
            y=[
                _line(-20, coef, intercept, i),
                _line(20, coef, intercept, i)
            ],
            mode='lines', 
            line={'color': COLOR[i], 'width': 2},
            name='Logistic Regression'
        ))

    layout = go.Layout(
        width=700,height=700,
        hovermode='closest', hoverdistance=1,
        xaxis={
            'title': 'Feature 1',
            'range': [-20,20],
            'fixedrange': True,
            'constrain': "domain",
            'scaleanchor': "y",
            'scaleratio': 1
        },
        yaxis={
            'title': 'Feature 2',
            'range': [-20,20],
            'fixedrange': True,
            'constrain': "domain"
        },
        paper_bgcolor='#FFFFFF',
        margin={'l': 30, 'r': 30, 't': 30, 'b': 30},
    )

    fig = go.Figure(data=data, layout=layout)
    state['figure'] = fig


initial_state = wf.init_state({
    "my_app": {
        "title": "Logistic regression visualizer"
    },
    "message": None,
    "figure": None,
    "multi_class": "ovr",
    "number_of_groups": 2,
    "number_of_points": 50,
    "cluster_std": 2,
})

update(initial_state)
