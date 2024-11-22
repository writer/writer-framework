import urllib
from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.core import BytesWrapper
from writer.ss_types import AbstractTemplate, WriterConfigurationError


class WriterAddToKG(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterAddToKG, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Add to Knowledge Graph",
                "description": "Adds files to an existing knowledge graph.",
                "category": "Writer",
                "fields": {
                    "graphId": {
                        "name": "Graph id",
                        "type": "Text",
                        "desc": "The id for an existing knowledge graph. It has a UUID format."
                    },
                    "files": {
                        "name": "Files",
                        "type": "Object",
                        "default": "[]",
                        "desc": "A list of files to be uploaded and added to the knowledge graph. You can use files uploaded via the File Input component or base64 strings."
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

    def run(self):
        try:
            import writer.ai

            graph_id = self._get_field("graphId", required=True)
            raw_files = self._get_field("files", as_json=True)
            files = []

            if not isinstance(raw_files, list):
                raise WriterConfigurationError("Files must be a list.")

            for raw_file in raw_files:
                if isinstance(raw_file, str):
                    urllib.request.urlopen(raw_file).read()
                elif isinstance(raw_file, bytes):
                    files.append(BytesWrapper(raw_file))
                

            # writer.ai.upload_file(data, type, name)

            # config = {}
            # if model_id:
            #     config["model"] = model_id

            # result = writer.ai.apps.generate_content(application_id, app_inputs).strip()
            # self.result = result
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e