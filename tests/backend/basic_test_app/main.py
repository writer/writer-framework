import writer as wf
from writer.ui import WriterUIManager
import asyncio

wf.Config.feature_flags = ["workflows"]
wf.Config.feature_flags.append("flag_one")
wf.Config.feature_flags.append("flag_two")

state = wf.get_state()
state.pet_count = 22
state.counter_middleware = 0
state.counter_post_middleware = 0
state.counter_middleware_without_yield = 0

def create_text_widget(ui: WriterUIManager):
    with ui.find("c0f99a9e-5004-4e75-a6c6-36f17490b134"):
        ui.Text({"text": "Hello world"})

async def sleep_and_greet():
    await asyncio.sleep(1)
    print("Hello, world!")

def bad_handler():
    return 1/0

def nineninenine():
    return 999

@wf.middleware()
def my_middleware(state):
    state.counter_middleware += 1
    yield

@wf.middleware()
def no_yield_middleware(state):
    state.counter_middleware_without_yield += 1

@wf.middleware()
def post_middleware(state):
    yield
    state.counter_post_middleware += 1