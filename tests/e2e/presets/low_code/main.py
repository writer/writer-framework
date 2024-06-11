import writer as wf

initial_state = wf.init_state({
    "value": "",
})

def update_value(state, payload):
    state['value'] = payload

def execute_test(state, ui):
    exec(state['code'])


with wf.init_ui() as ui:
    with ui.find('initialization'):
        ui.Text({"text": "Initialization successful!"});
