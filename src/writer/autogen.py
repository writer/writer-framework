import json
import dotenv
from writerai import Writer
import writer.abstract

dotenv.load_dotenv()

client = Writer()


block_definitions = []

for type, template in writer.abstract.templates.items():
    field_properties = {}
    for field_key, field in template.writer.get("fields", {}).items():
        field_properties[field_key] = {
            "type": "string",
            "description": f"Info about this field: {repr(field)}",
        }
    name = template.writer.get("name")
    description = template.writer.get("description")
    more_info = repr(template.writer)

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
            "description": f"Block name: {name} | Block description: {description}",
            "required": ["type", "id"],
            "additionalProperties": False,
            "properties": {
                "id": {
                    "type": "string",
                    "pattern": "^aig-\\d+$",
                    "description": "Unique identifier.",
                },
                "type": {"const": type},
                "content": {
                    "type": "object",
                    "properties": {
                        "alias": {
                            "type": "string",
                            "description": "A 1-5 word summary of what this block does.",
                        }
                    }
                    | field_properties,
                    "additionalProperties": False,
                },
                "outs": {
                    "type": "array",
                    "description": "The nodes that depend on this node, connected to each outcome of this node.",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["outId", "toNodeId"],
                        "properties": {
                            "outId": out_ids,
                            "toNodeId": {
                                "type": "string",
                                "pattern": "^aig-\\d+$",
                                "description": "The id of the node that'll be executed when this outcome takes place. Don't link to nodes that don't exist.",
                            },
                        },
                    },
                },
            },
        }
    )

tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_workflow",
            "description": "Generate a blueprint.",
            "parameters": {
                "type": "object",
                "properties": {
                    "components": {
                        "type": "array",
                        "items": {
                            "oneOf": block_definitions,
                        },
                    }
                },
            },
        },
    }
]

print(json.dumps(tools))
# exit()


def generate_workflow(workflow_description: str):
    prompt = (
        """

    <governing>

    You're a business analyst that's using the Writer Agent Editor, a solution that combines reusable blocks to get to an outcome.

    When an application integration node isn't available, use an HTTP request.

    The blocks are combined into what's called a blueprint or workflow.

    To use a value from state as part of a field, use the syntax @{my_var}, this will fetch the value "my_var" from state.

    All property or index access is via dots, for example @{my_arr.0.subprop} or @{my_obj.subprop}

    To get the result of the latest block, use @{result}, this will fetch the value from the execution environment, which is combined with state during runtime.

    Use logging sparingly. A "Log message" block cannot be referenced by more than 1 block. 

    All nodes must be connected to each other via "outs". Either they have something after them or a node depending on them.

    </governing>

    <task>

    Please generate a blueprint with the following characteristics

    -----

    """
        + workflow_description
        + """

    </task>

    """
    )
    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    response = client.chat.chat(
        model="palmyra-x5", messages=messages, tools=tools, tool_choice="required", stream=False
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    tool_call = tool_calls[0]
    print(tool_call.function.arguments)
    return json.loads(tool_call.function.arguments, strict=False)
