from uuid import uuid4

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate


class WriterUploadFile(WriterBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterUploadFile, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="blueprints_node",
            writer={
                "name": "Add files to Writer Cloud",
                "description": "Uploads files to the Writer platform.",
                "category": "Writer",
                "fields": {
                    "files": {
                        "name": "Files",
                        "type": "Object",
                        "default": "[]",
                        "desc": "A list of files to be uploaded and added to the knowledge graph. You can use files uploaded via the File Input component or specify dictionaries with data, type and name.",
                        "validator": {
                            "type": "array"
                        }
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "File successfully uploaded.",
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
        from writer.ai import WriterAIManager
        try:
            files = self._get_field("files", as_json=True, required=True)
            outputs = []
            if not isinstance(files, list):
                raise ValueError("Files must be a list.")
            for file in files:
                if not isinstance(file, dict):
                    raise ValueError("Files must be dictionaries and contain `data`, `type` and `name` attributes.")
                if "data" not in file or "type" not in file:
                    raise ValueError("A file specified as a dictionary must contain `data` and `type` attributes.")

                data = file.get("data")
                file_type = file.get("type")
                name = file.get("name")
                file_name = name or f"agent-builder-{file_type}-{uuid4()}"
                content_disposition = f'attachment; filename="{file_name}"'

                client = WriterAIManager.acquire_client()

                file = client.files.upload(
                    content=data,
                    content_type=file_type,
                    content_disposition=content_disposition
                    )

                outputs.append({
                    "id": file.id,
                    "name": file.name,
                    "status": file.status,
                    "created_at": file.created_at,
                    "graph_ids": file.graph_ids
                })
            if len(outputs) == 0:
                raise ValueError("No files were uploaded.")
            self.result = outputs
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
