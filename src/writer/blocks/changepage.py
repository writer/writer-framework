from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class ChangePage(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(ChangePage, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="workflows_node",
                writer={
                    "name": "Change page",
                    "description": "Changes the active page.",
                    "category": "Other",
                    "fields": {
                        "pageKey": {
                            "name": "Page key",
                            "type": "Text",
                            "desc": "The identifying key of the target page.",
                        },
                    },
                    "outs": {
                        "success": {
                            "name": "Success",
                            "description": "The page change was successful.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "The event handler execution wasn't successful.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        try:
            page_key = self._get_field("pageKey", required=True)
            self.runner.session.session_state.set_page(page_key)
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
