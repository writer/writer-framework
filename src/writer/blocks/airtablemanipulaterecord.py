import requests

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class AirtableManipulateRecord(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(AirtableManipulateRecord, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Airtable - Manipulate record",
                "description": "Performs operations on Airtable records.",
                "category": "Third parts",
                "fields": {
                    "apiKey": {
                        "name": "API Key",
                        "type": "Text",
                        "desc": "Your Airtable API key."
                    },
                    "base": {
                        "name": "Base",
                        "type": "Text",
                        "desc": "The ID of the base containing the table."
                    },
                    "table": {
                        "name": "Table",
                        "type": "Text",
                        "desc": "The name of the table to manipulate."
                    },
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            "create": "Create",
                            "update": "Update",
                            "remove": "Remove"
                        },
                        "default": "create"
                    },
                    "recordId": {
                        "name": "Record ID",
                        "type": "Text",
                        "desc": "The ID of the record to update or remove. Not required for create operations."
                    },
                    "fields": {
                        "name": "Fields",
                        "type": "Text",
                        "control": "Textarea",
                        "desc": "JSON string of fields and values to set.",
                        "default": "{}"
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The operation was successful.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "The operation failed.",
                        "style": "error",
                    },
                },
            }
        ))

    def run(self):
        try:
            api_key = self._get_field("apiKey", required=True)
            base = self._get_field("base", required=True)
            table = self._get_field("table", required=True)
            operation = self._get_field("operation", required=True)
            record_id = self._get_field("recordId", default_field_value="")
            payload = self._get_field("fields", as_json=True, default_field_value="{}")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = None

            if operation == "create":
                url = f"https://api.airtable.com/v0/{base}/{table}"
                response = requests.post(url, headers=headers, json={"fields": payload})
            elif operation == "update":
                url = f"https://api.airtable.com/v0/{base}/{table}/{record_id}"
                if not record_id:
                    raise ValueError("Record ID is required for update operations.")
                response = requests.patch(url, headers=headers, json={"fields": payload})
            elif operation == "remove":
                url = f"https://api.airtable.com/v0/{base}/{table}/{record_id}"
                if not record_id:
                    raise ValueError("Record ID is required for remove operations.")
                response = requests.delete(url, headers=headers)

            if response and response.ok:
                self.result = {
                    "id": response.json().get("id"),
                    "fields": response.json().get("fields")
                }
                self.outcome = "success"
            else:
                self.outcome = "error"
                response.raise_for_status()

        except BaseException as e:
            self.outcome = "error"
            raise e
