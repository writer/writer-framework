from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate


class WriterParsePDFByFileID(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterParsePDFByFileID, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Parse PDF tool",
                    "description": "Uses Writer API to extract the text content of a PDF file stored in Writer cloud.",
                    "category": "Writer",
                    "fields": {
                        "file": {
                                "name": "File",
                                "type": "Text",
                                "default": "",
                                "desc": "UUID of a file object in Files API.",
                                "validator": {
                                    "type": "string",
                                    "format": "uuid"
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

            file_uuid = self._get_field("file")
            markdown_input = self._get_field("markdown", False, "yes") == "yes"

            client = writer.ai.WriterAIManager.acquire_client()

            response = client.tools.parse_pdf(
                file_uuid,
                format="markdown" if markdown_input else "text"
            )

            self.result = response.content
            self.outcome = "success"

        except BaseException as e:
            self.outcome = "error"
            raise e
