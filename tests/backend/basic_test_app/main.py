import writer as wf
from writer.ui import WriterUIManager
import asyncio

wf.Config.feature_flags = ["workflows"]

pet_count = 22

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