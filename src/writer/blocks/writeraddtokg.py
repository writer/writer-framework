from typing import Any

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate, WriterConfigurationError


class WriterAddToKG(WriterBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterAddToKG, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="blueprints_node",
            writer={
                "name": "Add to Knowledge Graph",
                "description": "Adds structured information to the knowledge graph. Use for storing facts AI can reference.",
                "category": "Writer",
                "fields": {
                    "graphId": {
                        "name": "Graph Id",
                        "type": "Graph Id",
                        "desc": "The id for an existing knowledge graph. It has a UUID format.",
                        "validator": {
                            "type": "string",
                            "format": "uuid",
                        }
                    },
                    "files": {
                        "name": "Files",
                        "type": "Object",
                        "default": "[]",
                        "desc": "A list of files to be uploaded and added to the knowledge graph. You can use files uploaded via the File input component or specify dictionaries with data, type and name.",
                        "validator": {
                            "type": "array",
                        }
                    },
                    "urls": {
                        "name": "URLs",
                        "type": "Object",
                        "default": "[]",
                        "desc": "A list of URLs to be added to the knowledge graph. Web content from these URLs will be indexed.",
                        "validator": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "format": "uri",
                            }
                        }
                    },
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

    def _get_prepared_file(self, raw_file: Any):
        if not isinstance(raw_file, dict):
            raise WriterConfigurationError("Files must be dictionaries and contain `data`, `type` and `name` attributes.")

        if "data" not in raw_file or "type" not in raw_file or "name" not in raw_file:
            raise WriterConfigurationError("A file specified as a dictionary must contain `data`, `type` and `name` attributes.")

        return raw_file

    def run(self):
        try:
            import writer.ai

            graph_id = self._get_field("graphId", required=True)
            raw_files = self._get_field("files", as_json=True, default_field_value="[]")
            urls = self._get_field("urls", as_json=True, default_field_value="[]")
            prepared_files = []

            if not isinstance(raw_files, list):
                raise WriterConfigurationError("Files must be a list.")
            
            if not isinstance(urls, list):
                raise WriterConfigurationError("URLs must be a list.")
            
            if not raw_files and not urls:
                raise WriterConfigurationError("At least one file or URL must be provided.")

            for raw_file in raw_files:
                prepared_files.append(self._get_prepared_file(raw_file))
                
            graph = writer.ai.retrieve_graph(graph_id)
            
            # Add files to the graph
            for prepared_file in prepared_files:
                file = writer.ai.upload_file(prepared_file.get("data"),
                                             prepared_file.get("type"),
                                             prepared_file.get("name"))
                graph.add_file(file)
            
            # Add URLs to the graph using SDK 2.3.0 feature
            for url in urls:
                if not isinstance(url, str):
                    raise WriterConfigurationError(f"URL must be a string, got {type(url)}")
                graph.add_url(url)

            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
