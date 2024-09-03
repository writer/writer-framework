"""

Abstract templates.

They're used to register new component templates, based on existing frontend templates and a backend-provided component definition. 

"""

from typing import Dict

from writer.ss_types import AbstractTemplate

templates:Dict[str, AbstractTemplate]  = {}

def register_abstract_template(type: str, abstract_template: AbstractTemplate):
    templates[type] = abstract_template


register_abstract_template("wfssetstate", {
    "baseType": "workflowsnode",
    "writer": {
        "name": "Set state",
        "description": "Set the value for a state element",
        "category": "Content",
        "allowedParentTypes": ["workflow"],
        "fields": {
            "element": {
                "name": "State element",
                "type": "Text",
            },
            "value": {
                "name": "Value",
                "type": "Text",
            },
        },
        "outs": {
            "success": {
                "name": "Success",
                "description": "If the function doesn't raise an Exception.",
                "style": "success",
            },
            "error": {
                "name": "Error",
                "description": "If the function raises an Exception.",
                "style": "error",
            },
        },
    }
})