from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate


class WriterParsePDF(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterParsePDF, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Parse PDF Tool",
                    "description": "Uses Writer API to extract the text content of a PDF file.",
                    "category": "Writer",
                    "fields": {
                        "file": {
                                "name": "File",
                                "type": "Object",
                                "default": "{}",
                                "desc": "A file object to be parsed. You can use files uploaded via the File Input component or specify dictionaries with data, type and name.",
                                "validator": {
                                    "type": "object",
                                }
                            },
                        "markdown": {
                            "name": "Use Markdown",
                            "type": "Text",
                            "default": "yes",
                            "options": {"yes": "Yes", "no": "No"},
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
                },
            ),
        )

    def run(self):
        try:
            import writer.ai

            file_input = self._get_field("file", as_json=True)
            if isinstance(file_input, list):
                if len(file_input) != 1:
                    raise ValueError(
                        "File input must be a single file object."
                        )
                file_input = file_input[0]

            if not isinstance(file_input, dict):
                raise ValueError(
                    f"File input must be a dictionary: got {type(file_input)}."
                    )

            for key in ["type", "data"]:
                if key not in file_input:
                    raise ValueError(
                        f"File input must contain '{key}'."
                        )

            if "name" not in file_input:
                file_input["name"] = "untitled_file.pdf"

            if file_input.get("type") != "application/pdf":
                raise ValueError("File input must be a PDF file.")

            markdown_input = self._get_field("markdown", False, "yes") == "yes"

            prepared_file = writer.ai.upload_file(**file_input)

            client = writer.ai.WriterAIManager.acquire_client()

            response = client.tools.parse_pdf(
                prepared_file.id,
                format="markdown" if markdown_input else "text"
            )

            self.result = response.content
            self.outcome = "success"

        except BaseException as e:
            self.outcome = "error"
            raise e
