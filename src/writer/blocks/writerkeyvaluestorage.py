import re

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate

ALLOWED_CHARS = re.compile(r'^[A-Za-z0-9\-_]+$')


class WriterKeyValueStorage(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterKeyValueStorage, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Key-Value Storage",
                    "description": "Allows to store data between sessions. Uses unique keys (names) to identify the data. Keys can only contain alphanumeric characters, underscores and hyphens",
                    "category": "Writer",
                    "fields": {
                        "action": {
                            "name": "Action",
                            "type": "Text",
                            "description": "What action to perform on the data (save, get, delete).",
                            "options": {
                                "Save": "Save",
                                "Get": "Get",
                                "Delete": "Delete",
                            },
                            "default": "Save",
                        },
                        "key": {
                            "name": "Key",
                            "type": "Text",
                            "description": "Unique identifier of your data that will be used to retrieve, update and delete it.",
                        },
                        "value": {
                            "name": "Value",
                            "type": "Text",
                            "description": "Data that you want to store.",
                            "control": "Textarea",
                        }
                    },
                    "outs": {
                        "success": {
                            "name": "Success",
                            "description": "The request was successful.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "The request wasn't successful.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        from writer.keyvalue_storage import KeyValueStorage

        try:
            action = self._get_field("action", default_field_value="Save")
            key = self._get_field("key", required=True)
            if not ALLOWED_CHARS.fullmatch(key):
                raise ValueError("Key can only contain alphanumeric characters, underscores and hyphens")

            with self.acquire_httpx_client() as client:
                writer_kv_storage = KeyValueStorage(client=client)

                if action == "Save":
                    value = self._get_field("value")
                    response = writer_kv_storage.save(key, value)
                elif action == "Get":
                    response = writer_kv_storage.get(key, type_="data")
                elif action == "Delete":
                    response = writer_kv_storage.delete(key)
                else:
                    raise ValueError(f"Unknown action for the Key-Value Storage: {action}")

            self.result = response
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
