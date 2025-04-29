import json
import logging

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate


class WriterAskGraphQuestion(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterAskGraphQuestion, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="blueprints_node",
            writer={
                "name": "Ask graph question",
                "description": "Asks a natural language question using one or more knowledge graphs and puts the result into a state variable.",
                "category": "Writer",
                "fields": {
                    "question": {
                        "name": "Question",
                        "type": "Text",
                        "desc": "The natural language question to ask.",
                    },
                    "useStreaming": {
                        "name": "Use streaming",
                        "type": "Text",
                        "default": "yes",
                        "options": {
                            "yes": "Yes",
                            "no": "No"
                        },
                        "validator": {
                            "type": "string",
                            "enum": ["yes", "no"]
                        }
                    },
                    "stateElement": {
                        "name": "State Element",
                        "type": "Text",
                        "desc": "State variable to store or stream the response into. Reference the state element directly, i.e. use \"my_var\" instead of \"@{my_var}\".",
                    },
                    "graphIds": {
                        "name": "Graph Ids",
                        "type": "Object",
                        "desc": "IDs of the graphs to query.",
                        "default": "[]",
                        "validator": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "format": "uuid"
                            }
                        }
                    },
                    "subqueries": {
                        "name": "Use subqueries",
                        "type": "Text",
                        "desc": "Enables LLM to ask follow-up questions to the knowledge graph. This improves answers, but may be slower.",
                        "default": "no",
                        "options": {
                            "yes": "Yes",
                            "no": "No"
                        },
                        "validator": {
                            "type": "string",
                            "enum": ["yes", "no"]
                        }
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "Successfully streamed the answer.",
                        "style": "success"
                    },
                    "error": {
                        "name": "Error",
                        "description": "If the function raises an Exception.",
                        "style": "error"
                    }
                }
            }
        ))

    def run(self):
        try:
            client = self.writer_sdk_client

            graph_ids = self._get_field("graphIds", as_json=True, required=True)
            use_streaming = self._get_field("useStreaming", False, "yes") == "yes"
            if isinstance(graph_ids, str):
                graph_ids = [graph_ids]
            elif not isinstance(graph_ids, list):
                raise ValueError("graphIds must be a string or a list of strings")
            if len(graph_ids) == 0:
                raise ValueError("graphIds must not be empty")

            question = self._get_field("question", required=True)
            state_element = self._get_field("stateElement", required=False)
            if not state_element and use_streaming:
                raise ValueError("A state element must be provided when using streaming.")
            subqueries = self._get_field("subqueries", default_field_value="no") == "yes"

            answer_so_far = ""

            response = client.graphs.question(
                graph_ids=graph_ids,
                question=question,
                stream=use_streaming,
                subqueries=subqueries
            )
            if use_streaming:
                for chunk in response:
                    try:
                        delta = chunk.model_extra.get("answer", "")
                        answer_so_far += delta
                        self._set_state(state_element, answer_so_far)
                    except json.JSONDecodeError:
                        logging.error("Could not parse stream chunk from graph.question")
            else:
                answer_so_far = response.answer
                self._set_state(state_element, answer_so_far)

            self.result = answer_so_far
            self.outcome = "success"

        except BaseException as e:
            self.outcome = "error"
            raise e
