from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class WriterQuestionToKG(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterQuestionToKG, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Question Knowledge Graph",
                "description": "Ask a question to the knowledge graph.",
                "category": "Writer",
                "fields": {
                    "graphId": {
                        "name": "Graph ids",
                        "type": "Text",
                        "desc": "The ids for existing knowledge graphs. For multiple graphs, provide comma-separated UUIDs (e.g., 123e4567-e89b-12d3-a456-426614174000, 550e8400-e29b-41d4-a716-446655440000)",
                        "validator": {
                            "type": "string",
                        },
                    },
                    "question": {
                        "name": "Question",
                        "type": "Text",
                        "desc": "The question to ask the knowledge graph.",
                    },
                    "subqueries": {
                        "name": "Subqueries",
                        "type": "Text",
                        "desc": "Specify whether to include subqueries.",
                        "default": "no",
                        "options": {
                            "yes": "Yes",
                            "no": "No"
                        }
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "If the execution was successful.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "If the function raises an Exception.",
                        "style": "error",
                    },
                },
            }
        ))

    def run(self):
        try:
            import writer.ai
            
            graph_ids_str = self._get_field("graphId", required=True)
            graph_ids = [id.strip() for id in graph_ids_str.split(',')]
            question = self._get_field("question", required=True)
            stream = self._get_field("stream", default_field_value="no") == "yes"
            subqueries = self._get_field("subqueries", default_field_value="no") == "yes"

            client = writer.ai.WriterAIManager.acquire_client()
            response = client.graphs.question(
                graph_ids=graph_ids,
                question=question,
                stream=False,
                subqueries=subqueries
            )
            self.result = response
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
