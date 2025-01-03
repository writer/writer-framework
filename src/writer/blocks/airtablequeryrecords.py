import requests

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class AirtableQueryRecords(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(AirtableQueryRecords, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Query records",
                "description": "Queries records from an Airtable table based on a provided formula.",
                "category": "Third parts",
                "group": "Airtable",
                "fields": {
                    "table": {
                        "name": "Table",
                        "type": "Text",
                        "desc": "The name of the table to query."
                    },
                    "formula": {
                        "name": "Formula",
                        "type": "Text",
                        "desc": "The Airtable formula to filter records."
                    },
                    "sortFields": {
                        "name": "Sort Fields",
                        "type": "Text",
                        "desc": "Fields to sort by, formatted as a JSON array of objects with 'field' and 'direction'."
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
            formula = self._get_field("formula")
            sort_fields = self._get_field("sortFields", as_json=True, default_field_value="[]")

            headers = {
                "Authorization": f"Bearer {api_key}"
            }

            params = {
                "filterByFormula": formula,
            }

            for i, sort_item in enumerate(sort_fields):
                params[f"sort[{i}][field]"] = sort_item["field"]
                params[f"sort[{i}][direction]"] = sort_item["direction"]

            url = f"https://api.airtable.com/v0/{base}/{table}"
            response = requests.get(url, headers=headers, params=params)

            if response.ok:
                records = response.json().get("records", [])
                self.result = [{"recordId": rec.get("id"), "fields": rec.get("fields")} for rec in records]
                self.outcome = "success"
            else:
                self.outcome = "error"
                response.raise_for_status()

        except BaseException as e:
            self.outcome = "error"
            raise e

