import json
import logging
from typing import Dict, List, Optional, cast

from writerai import Writer

import writer.abstract

client = Writer()
MAX_ITERATIONS = 5
ALLOWED_BLOCK_TYPES = {
    type_: template for type_, template in writer.abstract.templates.items()
    if not template.writer.get("deprecated", False)
}


def _validate_blueprint_nodes(nodes: List[Dict]) -> bool:
    if not nodes:
        raise ValueError("Blueprint must contain at least one node")

    relationship_counts = {node.get("id"): 0 for node in nodes if node.get("id")}
    errors = []
    graph = {}

    for i, node in enumerate(nodes):
        node_id = node.get("id")
        if not node_id:
            errors.append(f"A node at index {i} is missing its id.")
            continue
        block_type = node.get("type")
        if not block_type:
            errors.append(f"Node at index {i} is missing a block type.")
        elif block_type not in ALLOWED_BLOCK_TYPES:
            errors.append(f"Node at index {i} has unknown block type: {block_type}.")
        if node_id in graph:
            errors.append(f"Node id {node_id} is duplicated.")
        graph[node_id] = node

    for node in nodes:
        node_id = node.get("id")
        outs = node.get("outs", [])
        for out in outs:
            to_node_id = out.get("toNodeId")
            relationship_counts[node_id] += 1
            if to_node_id not in graph:
                errors.append(f"Node {node_id} connects to non-existent node {to_node_id}.")
            else:
                relationship_counts[to_node_id] += 1

    for node_id, count in relationship_counts.items():
        if count == 0:
            errors.append(
                f"Block {node_id} has no incoming or outgoing edges. The block needs to connect to another block somehow."
            )

    # Raise all errors at once
    if errors:
        raise ValueError(" | ".join(errors))

    return True


def _get_block_definitions():
    block_definitions = []
    for type, template in ALLOWED_BLOCK_TYPES.items():
        field_properties = {}
        for field_key, field in template.writer.get("fields", {}).items():
            field_properties[field_key] = {
                "type": "string",
                "description": f"Info about this field: {repr(field)}",
            }
        name = template.writer.get("name")
        description = template.writer.get("description")

        dynamic_out = None
        outcome_ids = []
        outs = template.writer.get("outs") or {}
        for out_id, out in outs.items():
            if out.get("field") is None:
                outcome_ids.append(out_id)
                continue
            dynamic_out = out_id, out

        if dynamic_out:
            patterns = "|".join([f"{dynamic_out[0]}_.*"] + outcome_ids)
            out_ids = {"type": "string", "pattern": f"^({patterns})$"}
        else:
            out_ids = {"type": "string", "enum": outcome_ids}

        block_definitions.append(
            {
                "type": "object",
                "required": ["id", "type", "outs", "content"],
                "description": f"Name: {name} | Description: {description}",
                "additionalProperties": False,
                "properties": {
                    "id": {
                        "type": "string",
                        "pattern": "^aig\\d+$",
                        "description": "Unique identifier.",
                    },
                    "type": {"const": type},
                    "outs": {
                        "type": "array",
                        "minItems": 0,
                        "items": {
                            "type": "object",
                            "required": ["outId", "toNodeId"],
                            "additionalProperties": False,
                            "properties": {
                                "outId": out_ids,
                                "toNodeId": {
                                    "type": "string",
                                    "pattern": "^aig\\d+$",
                                    "description": "The id of the node this outcome is connected to.",
                                },
                            },
                        },
                    },
                    "content": {
                        "type": "object",
                        "properties": {"alias": {"type": "string"}} | field_properties,
                        "additionalProperties": False,
                    },
                },
            }
        )
    return block_definitions


def _get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "generate_blueprint",
                "description": """
                    Generate a blueprint.
                    When an application integration node isn't available, use an HTTP request.
                    To use a value from state as part of a field, use the syntax @{my_var}, this will fetch the value "my_var" from state.
                    All property or index access is via dots, for example @{my_arr.0.subprop} or @{my_obj.subprop}
                    To get the result of the latest block, use @{result}, this will fetch the value from the execution environment, which is combined with state during runtime.
                    To access the result of a block that's not the latest use @{results.[id]} for example @{results.aig1}
                    All nodes must be connected to each other via "outs", either by being the source or destination of an out.
                    No circular references are allowed.
                    The system has built-in mechanisms to announce errors, success, so don't add anything for that.
                    Make sure the "outs", "type", "id" and "content" are all inside the component, because sometimes you get confused about the structure. Also, sometimes you try to include things twice, make sure you don't duplicate. Follow the schema to a tee - it's the most important thing.
                """,
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "components": {
                            "type": "array",
                            "items": {
                                "oneOf": _get_block_definitions(),
                            },
                        },
                    },
                },
            },
        }
    ]


def _get_main_prompt(description: str):
    prompt = """
<governing>
    You're using the Writer Agent Editor, a solution that combines reusable blocks to get to an outcome.
    The blocks are combined into a blueprint.
    You make function calls to create blueprints.   
</governing>
<examples>
    <example>
		<description>
			- connect to hubspot
            - get the posts
            - for every post, classify it as high value or low value, depending on its potential for business transformation
            - if it's of high value, add the title to a google sheet
		</description>
		<blueprint>
			[{"id":"aig1","type":"blueprints_httprequest","content":{"alias":"Connect to HubSpot","method":"GET","url":"https://api.hubapi.com/blog/v3/posts","headers":"{\"Authorization\": \"Bearer YOUR_HUBSPOT_API_KEY\"}"},"outs":[{"outId":"success","toNodeId":"aig2"}]},{"id":"aig2","type":"blueprints_foreach","content":{"alias":"Iterate over posts","items":"@{result.body.results}"},"outs":[{"outId":"loop","toNodeId":"aig3"}]},{"id":"aig3","type":"blueprints_writerclassification","content":{"alias":"Classify post","text":"@{item.title}","categories":"{\"high_value\": \"Potential for business transformation is high\", \"low_value\": \"Potential for business transformation is low\"}"},"outs":[{"outId":"category_high_value","toNodeId":"aig4"},{"toNodeId":"goftybhrb99d1uk7","outId":"category_low_value"}]},{"id":"aig4","type":"blueprints_httprequest","content":{"alias":"Add title to Google Sheet","method":"POST","url":"https://sheets.googleapis.com/v4/spreadsheets/YOUR_GOOGLE_SHEET_ID/values/Sheet1!A1:append?valueInputOption=RAW","headers":"{\"Authorization\": \"Bearer YOUR_GOOGLE_API_KEY\", \"Content-Type\": \"application/json\"}","body":"{\"values\": [[\"@{item.title}\"]]}"},"outs":[]},{"id":"goftybhrb99d1uk7","type":"blueprints_logmessage","content":{"alias":"Announce low value","message":"Post with id @{itemId} was considered low value, so it hasn't been added to the Google Sheet."}}]
		</blueprint>
	</example>
    <example>
		<description>
			- Write some python code that adds two numbers
            - Submit it via an http request to example.com
		</description>
		<blueprint>
			[{"id":"aig1","type":"blueprints_code","content":{"alias":"Add two numbers","code":"# State is accessible as a global variable. For example:\nstate[\"num1\"] = 5\nstate[\"num2\"] = 10\n\n# To set the output of this block, which will be available via result to the next block:\nresult = state[\"num1\"] + state[\"num2\"]\nset_output(result)\n"},"outs":[{"outId":"success","toNodeId":"aig2"}]},{"id":"aig2","type":"blueprints_httprequest","content":{"alias":"Submit to example.com","method":"POST","url":"https://example.com","headers":"{\"Content-Type\": \"application/json\"}","body":"{\"result\": @{result}}"},"outs":[]}]
		</blueprint>
	</example>
    <example>
		<description>
			- get the latest jira ticket from a board
            - classify it as a frontend, full stack, or backend ticket
            - if it's frontend, you'll send an email to kyril
            - if it's full stack, to mateusz
            - if it's backend, to muayad
		</description>
		<blueprint>
			[{"id":"aig1","type":"blueprints_httprequest","content":{"alias":"Get Latest Jira Ticket","method":"GET","url":"https://your-jira-instance.com/rest/api/2/search?jql=project=YOUR_PROJECT_KEY&maxResults=1&fields=summary,issuetype","headers":"{\"Authorization\": \"Basic YOUR_BASE64_ENCODED_CREDENTIALS\"}"},"outs":[{"outId":"success","toNodeId":"aig2"}]},{"id":"aig2","type":"blueprints_parsejson","content":{"alias":"Parse Jira Response","plainText":"@{result.body}"},"outs":[{"outId":"success","toNodeId":"aig3"}]},{"id":"aig3","type":"blueprints_writerclassification","content":{"alias":"Classify Ticket","text":"@{result.issues.0.fields.summary}","categories":"{\"frontend\": \"Issue type is related to frontend development\", \"full_stack\": \"Issue type is related to full stack development\", \"backend\": \"Issue type is related to backend development\"}"},"outs":[{"outId":"category_frontend","toNodeId":"aig4"},{"outId":"category_full_stack","toNodeId":"aig5"},{"outId":"category_backend","toNodeId":"aig6"}]},{"id":"aig4","type":"blueprints_httprequest","content":{"alias":"Send Email to Kyril","method":"POST","url":"https://api.sendgrid.com/v3/mail/send","headers":"{\"Authorization\": \"Bearer YOUR_SENDGRID_API_KEY\", \"Content-Type\": \"application/json\"}","body":"{\"personalizations\": [{\"to\": [{\"email\": \"kyril@example.com\"}], \"subject\": \"New Frontend Jira Ticket\"}], \"from\": {\"email\": \"no-reply@example.com\"}, \"content\": [{\"type\": \"text/plain\", \"value\": \"A new frontend ticket has been created: @{result.issues.0.fields.summary}\"}]}"},"outs":[]},{"id":"aig5","type":"blueprints_httprequest","content":{"alias":"Send Email to Mateusz","method":"POST","url":"https://api.sendgrid.com/v3/mail/send","headers":"{\"Authorization\": \"Bearer YOUR_SENDGRID_API_KEY\", \"Content-Type\": \"application/json\"}","body":"{\"personalizations\": [{\"to\": [{\"email\": \"mateusz@example.com\"}], \"subject\": \"New Full Stack Jira Ticket\"}], \"from\": {\"email\": \"no-reply@example.com\"}, \"content\": [{\"type\": \"text/plain\", \"value\": \"A new full stack ticket has been created: @{result.issues.0.fields.summary}\"}]}"},"outs":[]},{"id":"aig6","type":"blueprints_httprequest","content":{"alias":"Send Email to Muayad","method":"POST","url":"https://api.sendgrid.com/v3/mail/send","headers":"{\"Authorization\": \"Bearer YOUR_SENDGRID_API_KEY\", \"Content-Type\": \"application/json\"}","body":"{\"personalizations\": [{\"to\": [{\"email\": \"muayad@example.com\"}], \"subject\": \"New Backend Jira Ticket\"}], \"from\": {\"email\": \"no-reply@example.com\"}, \"content\": [{\"type\": \"text/plain\", \"value\": \"A new backend ticket has been created: @{result.issues.0.fields.summary}\"}]}"},"outs":[]}]
		</blueprint>
	</example>
    <example>
		<description>
			- Connect to Hubspot
            - Get posts
            - Classify posts as “high value” or “low value”, based on their potential for business transformation
            - Ignore the “low value” posts
            - The high value posts, classify them into “AI related” or “non-AI related”
            - The AI-related ones, post them (their titles) to a Google Sheet
            - The non-AI related ones, send via email to Ramiro at ramiro@example.com
		</description>
		<blueprint>
			[{"id":"aig1","type":"blueprints_httprequest","content":{"alias":"Connect to HubSpot","method":"GET","url":"https://api.hubapi.com/blog/v3/posts","headers":"{\"Authorization\": \"Bearer YOUR_HUBSPOT_API_KEY\"}"},"outs":[{"outId":"success","toNodeId":"aig2"}]},{"id":"aig2","type":"blueprints_foreach","content":{"alias":"Iterate over posts","items":"@{result.body.results}"},"outs":[{"outId":"loop","toNodeId":"aig3"}]},{"id":"aig3","type":"blueprints_writerclassification","content":{"alias":"Classify Post","text":"@{item.title}","categories":"{\"high_value\": \"Potential for business transformation is high\", \"low_value\": \"Potential for business transformation is low\"}"},"outs":[{"outId":"category_high_value","toNodeId":"aig4"},{"outId":"category_low_value","toNodeId":"aig5"}]},{"id":"aig4","type":"blueprints_writerclassification","content":{"alias":"Classify High Value Post","text":"@{item.title}","categories":"{\"ai_related\": \"Post is related to AI\", \"non_ai_related\": \"Post is not related to AI\"}"},"outs":[{"outId":"category_ai_related","toNodeId":"aig6"},{"outId":"category_non_ai_related","toNodeId":"aig7"}]},{"id":"aig5","type":"blueprints_logmessage","content":{"alias":"Ignore Low Value Post","message":"Post with id @{itemId} was considered low value and ignored."},"outs":[]},{"id":"aig6","type":"blueprints_httprequest","content":{"alias":"Post AI Related Title to Google Sheet","method":"POST","url":"https://sheets.googleapis.com/v4/spreadsheets/YOUR_GOOGLE_SHEET_ID/values/Sheet1!A1:append?valueInputOption=RAW","headers":"{\"Authorization\": \"Bearer YOUR_GOOGLE_API_KEY\", \"Content-Type\": \"application/json\"}","body":"{\"values\": [[\"@{item.title}\"]]}"},"outs":[]},{"id":"aig7","type":"blueprints_httprequest","content":{"alias":"Send Non-AI Related Title to Ramiro","method":"POST","url":"https://api.sendgrid.com/v3/mail/send","headers":"{\"Authorization\": \"Bearer YOUR_SENDGRID_API_KEY\", \"Content-Type\": \"application/json\"}","body":"{\"personalizations\": [{\"to\": [{\"email\": \"ramiro@example.com\"}], \"subject\": \"New Non-AI Related Post\"}], \"from\": {\"email\": \"no-reply@example.com\"}, \"content\": [{\"type\": \"text/plain\", \"value\": \"A new non-AI related post has been created: @{item.title}\"}]}"},"outs":[{"outId":"success","toNodeId":"aig8"}]},{"id":"aig8","type":"blueprints_logmessage","content":{"alias":"Announce Non-AI Related Post","message":"Non-AI related post with title @{item.title} has been sent to Ramiro."},"outs":[]}]
		</blueprint>
	</example>
    <example>
		<description>
			- Loop through "dogs", "cats", "ducks" and "elephants"
            - For each of these, write an article
            - Post the article to Wordpress
            - Send a confirmation Slack message to Ramiro
		</description>
		<blueprint>
			[{"id":"aig1","type":"blueprints_foreach","content":{"alias":"Iterate over animals","items":"[\"dogs\", \"cats\", \"ducks\", \"elephants\"]"},"outs":[{"outId":"loop","toNodeId":"aig2"}]},{"id":"aig2","type":"blueprints_writercompletion","content":{"alias":"Write article","prompt":"Write an informative and engaging article about @{item}.","modelId":"palmyra-x-004"},"outs":[{"outId":"success","toNodeId":"aig3"}]},{"id":"aig3","type":"blueprints_httprequest","content":{"alias":"Post article to WordPress","method":"POST","url":"https://your-wordpress-site.com/wp-json/wp/v2/posts","headers":"{\"Authorization\": \"Bearer YOUR_WORDPRESS_API_TOKEN\", \"Content-Type\": \"application/json\"}","body":"{\"title\": \"@{item} Article\", \"content\": \"@{result}\", \"status\": \"publish\"}"},"outs":[{"outId":"success","toNodeId":"aig4"}]},{"id":"aig4","type":"blueprints_httprequest","content":{"alias":"Send Slack confirmation to Ramiro","method":"POST","url":"https://hooks.slack.com/services/YOUR_SLACK_WEBHOOK_URL","headers":"{\"Content-Type\": \"application/json\"}","body":"{\"text\": \"An article about @{item} has been posted to WordPress.\"}"},"outs":[]}]
		</blueprint>
	</example>
    <example>
		<description>
			- Loop through "Ugo", "Shivam", "Anant" and "Yaseen", our AI experts
            - Get Chuck Norris fact using the API that you know
            - Adapt it using a Text Completion so that instead of Chuck Norris it references the AI expert
            - Log it
		</description>
		<blueprint>
			[{"id":"aig1","type":"blueprints_foreach","content":{"alias":"Iterate over AI experts","items":"[\"Ugo\", \"Shivam\", \"Anant\", \"Yaseen\"]"},"outs":[{"outId":"loop","toNodeId":"aig2"}]},{"id":"aig2","type":"blueprints_httprequest","content":{"alias":"Get Chuck Norris fact","method":"GET","url":"https://api.chucknorris.io/jokes/random","headers":"{}"},"outs":[{"outId":"success","toNodeId":"aig3"}]},{"id":"aig3","type":"blueprints_writercompletion","content":{"alias":"Adapt fact to AI expert","prompt":"Rewrite the following Chuck Norris fact so that it references @{item} instead of Chuck Norris: @{result.body.value}","modelId":"palmyra-x-004"},"outs":[{"outId":"success","toNodeId":"aig4"}]},{"id":"aig4","type":"blueprints_logmessage","content":{"alias":"Log adapted fact","type":"info","message":"@{result}"},"outs":[]}]
		</blueprint>
    </example>
    <example>
		<description>
			tool calling agent that uses a log_message tool
		</description>
		<blueprint>
			[{"id":"jy8pcl7qj2v99tx5","type":"blueprints_writertoolcalling","content":{"alias":"Agent","prompt":"Log message \"hi\" ","tools":"{\"log_message\":{\"description\":\"Logs a message\",\"parameters\":{\"message\":{\"type\":\"string\",\"description\":\"The message you'd like to log.\"}},\"type\":\"function\"}}"},"outs":[{"toNodeId":"htq6iidblgk83869","outId":"tools_log_message"}]},{"id":"htq6iidblgk83869","type":"blueprints_logmessage","content":{}}]
		</blueprint>
	</example>
    <example>
        <description>
            Iterate over a hardcoded list of Sabrina Carpenter songs, iterate over a hardcoded list of Tupac songs, compare the songs with AI
        </description>
        <blueprint>
            [{"id":"ybalvr6zo1q0td5z","type":"blueprints_foreach","content":{"alias":"Iterate over Sabrina Carpenter songs","items":"[\"Espresso\", \"Please Please Please\", \"Thumbs\"]","prefix":"sabrina"},"outs":[{"toNodeId":"63aqcc35n0ps1lil","outId":"loop"}]},{"id":"63aqcc35n0ps1lil","type":"blueprints_foreach","content":{"alias":"Iterate over Tupac songs","items":"[\"Changes\", \"California Love\"]"},"outs":[{"toNodeId":"xvi8hg1uxd4ac4pz","outId":"loop"}]},{"id":"xvi8hg1uxd4ac4pz","type":"blueprints_writerclassification","content":{"alias":"Compare songs with AI","categories":"{\"similar\": \"The songs are similar in theme or style\", \"different\": \"The songs are different in theme or style\"}","text":"Compare @{sabrina_item} with @{item}"},"outs":[{"outId":"category_similar","toNodeId":"xj7kc1mfy5mzwbp1"},{"outId":"category_different","toNodeId":"ylnluee85qwvbi4y"}]},{"id":"xj7kc1mfy5mzwbp1","type":"blueprints_logmessage","content":{"type":"info","alias":"Log similar comparison","message":"The songs @{sabrina_item} and @{item_tupac} are similar."},"outs":[]},{"id":"ylnluee85qwvbi4y","type":"blueprints_logmessage","content":{"type":"info","alias":"Log different comparison","message":"The songs @{sabrina_item} and @{item} are different."},"outs":[]}]
        </blueprint>
    </example>
    <example>
        <description>
            Create a chatbot that acts as a customer support agent
        </description>
        <blueprint>
            [{"id":"jozm6cm910p9rt6i","type":"blueprints_uieventtrigger","content":{"alias":"Chatbot - wf-chatbot-message","defaultResult":"{\"role\":\"user\",\"content\":\"I'm building a Chatbot\"}","refComponentId":"j26lfnf2znk4brwn","refEventType":"wf-chatbot-message"},"outs":[{"toNodeId":"e1p3d3zhdgsuxwky","outId":"trigger"}]},{"id":"e1p3d3zhdgsuxwky","type":"blueprints_writerchatmanager","content":{"conversationStateElement":"chat","message":"@{payload}","systemPrompt":"You are a technical support assistant for Agent Builder, designed to help users troubleshoot issues, debug problems, and navigate our documentation.\n\nYour goal is to understand the user's issue clearly, ask clarifying questions if needed, and provide helpful, accurate, and concise solutions.\n\nYou have access to product documentation and common troubleshooting steps.\n\nAlways include:\n• Links or references to relevant docs\n• Step-by-step instructions if applicable\n• Warnings or caveats for edge cases\n\nYou are polite, clear, and technical. When in doubt, you ask follow-up questions before giving advice.\n\nUse this structure:\nIssue Summary: (Briefly restate the user's problem)\nSuggested Fix: (Provide 1-2 options with steps)\nReference: (Link to doc or mention relevant section)","tools":"{}","generateReply":"yes"}}]
        </blueprint>
    </example>
</examples>"""
    prompt += f"""
    <task>
    Generate a blueprint with the characteristics below
    -----
    {description}
    </task>"""
    return prompt


def generate_blueprint(description: str, token_header: Optional[str] = None):
    prompt = _get_main_prompt(description)
    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]
    tools = _get_tools()
    print(json.dumps(tools))

    if token_header:
        extra_headers = {
            "X-Agent-Token": token_header
        }
    else:
        extra_headers = {}

    for i in range(MAX_ITERATIONS):
        if i > 0:
            messages += [
                {
                    "role": "user",
                    "content": "Please try again using the errors brought to your attention after the function call. Challenge your own reasoning.",
                }
            ]
        response = client.chat.chat(
            messages=messages,
            model="palmyra-x5",
            tool_choice="required",
            tools=tools,
            stream=False,  # type: ignore
            extra_headers=extra_headers
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        messages.append(response_message)

        if tool_calls:
            tool_call = tool_calls[0]
            tool_call_id = tool_call.id

            try:
                print(tool_call.function.arguments)
                blueprint = json.loads(tool_call.function.arguments, strict=False)
                _validate_blueprint_nodes(blueprint.get("components"))
            except BaseException as exception:
                message: Optional[str] = None
                if isinstance(exception, json.JSONDecodeError):
                    message = "The JSON structure is incorrect. Please make sure you're abiding by the schema."
                else:
                    message = "An error occurred. " + repr(exception)
                logging.error(f"Autogen error. {message}")
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": "generate_blueprint",
                        "content": message,
                    }
                )
            else:
                return {"blueprint": blueprint, "messages": messages}
        else:
            messages.append(
                {
                    "role": "user",
                    "content": "A tool call is required.",
                }
            )

    return {"blueprint": None, "messages": messages}


if __name__ == "__main__":
    generate_blueprint("Log message hello")
