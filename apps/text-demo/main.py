import re

import writer as wf
import writer.ai

# Welcome to Writer Framework! 
# This is a simple app to get you started with text completion.
# More documentation is available at https://dev.writer.com

def handle_button_click(state):
    state["message"] = "% Loading up expert social media posts..."
    
    prompt = f"You are a social media expert. Generate 5 engaging social media posts about {state['topic']}. Include emojis."
    state["posts"] = writer.ai.complete(prompt)

    prompt = f"You are a social media expert. Generate 5 hashtags about {state['topic']}, delimited by spaces. For example, #dogs #cats #ducks #elephants #badgers"
    pattern = r'#\w+'
    hashtags = re.findall(pattern, writer.ai.complete(prompt))
    state["tags"] = {item: item for item in hashtags}
    
    state["message"] = ""

# Initialize state here

wf.init_state({
    "posts": "",
    "topic": "writing",
    "message": ""
})