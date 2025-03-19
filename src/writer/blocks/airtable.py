from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class Airtable(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(Airtable, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node_group",
            writer={
                "name": "Airtable",
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
                }
            }
        ))

    def run(self):
        self.result = {
            "msg": "Not implemented"
        }
        self.outcome = "error"
