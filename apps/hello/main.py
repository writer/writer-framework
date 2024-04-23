import statistics

import numpy as np
import pandas as pd
import plotly.express as px
import streamsync as ss
from streamsync.core import StreamsyncState

# EVENT HANDLERS

def handle_timer_tick(state: StreamsyncState):
    df = state["random_df"]
    for i in range(5):
        df[f'pgcf_{i+1}'] = np.around(np.random.rand(10, 1), decimals=9)
    state["random_df"] = df


def update(state, session):
    main_df = _get_main_df()
    main_df = main_df[main_df['length_cm'] >= state["filter"]["min_length"]]
    main_df = main_df[main_df['weight_g'] >= state["filter"]["min_weight"]]
    state['main_df'] = main_df

    paginated_members = _get_paginated_members(state['paginated_members_page'] - 1, state['paginated_members_page_size'])
    state['paginated_members'] = paginated_members
    state["session"] = session
    _update_metrics(state)
    _update_role_chart(state)
    _update_scatter_chart(state)


def handle_story_download(state):
    data = ss.pack_file("assets/story.txt", "text/plain")
    file_name = "hacker_pigeons.txt"
    state.file_download(data, file_name)


def handle_paginated_members_page_change(state, payload):
    page = payload
    maxpage = int(state["paginated_members_total_items"] / state["paginated_members_page_size"]) + 1
    if page > maxpage:
        state["paginated_members_page"] = maxpage - 2
    else:
        state["paginated_members_page"] = page

    update(state, None)


def handle_paginated_members_page_size_change(state, payload):
    state['paginated_members_page_size'] = payload
    update(state, None)


# LOAD / GENERATE DATA


def _generate_random_df():
    data = np.around(np.random.rand(10, 5), decimals=9)
    column_names = [f'pgcf_{i+1}' for i in range(5)]
    random_df = pd.DataFrame(data, columns=column_names)
    return random_df


def _get_main_df():
    main_df = pd.read_csv("assets/main_df.csv")
    return main_df

def _get_highlighted_members():
    sample_df = _get_main_df().sample(3).set_index("name", drop=False)
    sample = sample_df.to_dict("index")
    return sample

def _get_paginated_members(offset: int, limit: int):
    paginated_df = _get_main_df()[offset:offset + limit].set_index("name", drop=False)
    paginated = paginated_df.to_dict("index")
    return paginated

def _get_story_text():
    with open("assets/story.txt", "r") as f:
        return f.read()

def handle_chat_message(payload, state):
    if payload == "pdf":
        return {
            "text": "In this demo you can find only this PDF file.",
            "actions": [{
                "subheading": "Resource",
                "name": "Neon Feathers",
                "desc": "Click to open",
                "data": "open_pdf" 
            }]
        }
    elif payload == "web":
        return {
            "text": "In this demo you can find only this web link.",
            "actions": [{
                "subheading": "Resource",
                "name": "Streamsync",
                "desc": "Click to open",
                "data": "open_web" 
            }]
        }

    elif payload == "highlight" and state["chat_bot"]["show_pdf"]:
        state["chat_bot"]["pdf"]["highlights"] = ["FeatherByte", "SynthoCorp"]
        return "I have highlighted some interesting parts of the story."
    elif payload == "help":
        return "You can type `pdf` or `web` to see what these components can do."
    else:
        return "I don't understand that command. Type 'help' to see what is possible."

def _show_chatbot_resource(name, resource, state):
    if name == "pdf":
        state["chat_bot"]['pdf']['source'] = resource
        state["chat_bot"]["show_pdf"] = True
        state["chat_bot"]["show_web"] = False
    elif name == "web":
        state["chat_bot"]['web']['url'] = resource
        state["chat_bot"]["show_pdf"] = False
        state["chat_bot"]["show_web"] = True

def handle_chat_action(payload, state):
    if payload == "open_pdf":
        _show_chatbot_resource("pdf", "static/neon_feathers.pdf", state)
        return "I hope you will enjoy the story. Now you can type `highlight` to see what I can show you."
    if payload == "open_web":
        _show_chatbot_resource("web", "https://streamsync.cloud/", state)
        return {
            "text": "This is Streamsync documentation. You can find more information about Streamsync here.",
            "actions": [{
                "subheading": "Resource",
                "name": "Components",
                "desc": "Click to open",
                "data": "open_web_components" 
            }, {
                "subheading": "Tutorial",
                "name": "Quick start",
                "desc": "Click to open",
                "data": "open_web_tutorial" 
            }]
        }
    if payload == "open_web_components":
        _show_chatbot_resource("web", "https://streamsync.cloud/component-list.html", state)
        return "You can find all components here."
    if payload == "open_web_tutorial":
        _show_chatbot_resource("web", "https://www.streamsync.cloud/component-list.html", state)
        return "You can find quick start tutorial here."

    return "I don't understand that command. Type 'help' to see what is possible."

# UPDATES


def _update_metrics(state):
    main_df = state["main_df"]
    bmi_list = (main_df['weight_g'] / 1000) / \
        ((main_df['length_cm'] / 100) ** 2)
    bmi = statistics.mean(bmi_list)
    diversity_index = main_df['feather_color'].nunique()/len(main_df)
    metrics = {
        "average_weight": round(main_df['weight_g'].mean(), 0),
        "average_length": round(main_df['length_cm'].mean(), 0),
        "average_bmi": round(bmi, 2),
        "diversity": round(diversity_index, 2),
    }
    metrics.update({
        "average_weight_note": "+Acceptable",
        "average_length_note": "+Acceptable",
        "average_bmi_note": "-Overweight" if metrics["average_bmi"] >= 5.2 else "+Acceptable",
        "diversity_note": "-Not diverse" if metrics["diversity"] < 0.8 else "+Acceptable",
    })
    state["metrics"] = metrics


def _update_role_chart(state):
    main_df = state["main_df"]
    custom_color_scale = ["#dd43df", "#e057e7",
                          "#e36bef", "#e680f7", "#e994ff"]
    role_counts = main_df['role'].value_counts().reset_index()
    role_counts.columns = ['role', 'count']
    fig = px.bar(role_counts, x='role', y='count', color='role',
                 color_discrete_sequence=custom_color_scale)
    fig.update_layout(
        margin={"l": 20, "r": 20, "t": 20, "b": 50},
        showlegend=False
    )
    state["role_chart"] = fig


def _update_scatter_chart(state):
    main_df = state["main_df"]
    average_role_data = main_df.groupby("role").agg(
        {"length_cm": "mean", "weight_g": "mean"}).reset_index()
    fig = px.scatter(average_role_data, x="length_cm", y="weight_g",
                     color="role", height=400, size_max=10, size="weight_g")
    fig.update_layout(
        margin={"l": 20, "r": 20, "t": 20, "b": 50},
        showlegend=False
    )
    state["scatter_chart"] = fig

# STATE INIT


initial_state = ss.init_state({
    "main_df": _get_main_df(),
    "highlighted_members": _get_highlighted_members(),
    "random_df": _generate_random_df(),
    "hue_rotation": 26,
    "paginated_members": _get_paginated_members(0, 2),
    "paginated_members_page": 1,
    "paginated_members_total_items": len(_get_main_df()),
    "paginated_members_page_size": 2,
    "story": {
        "text": _get_story_text(),  # For display
    },
    "filter": {
        "min_length": 25,
        "min_weight": 300,
    },
    "metrics": {},
    "chat_bot": {
        "show_web": False,
        "show_pdf": False,
        "pdf": {
            "source": "",
        },
        "web": {
            "url": "",
        },
    }
})

update(initial_state, None)
