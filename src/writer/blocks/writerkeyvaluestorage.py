import re

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate, WriterConfigurationError

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
                    "description": "Stores data between sessions. Uses unique keys (names) to identify the data. Keys can only contain alphanumeric characters, underscores, and hyphens.",
                    "category": "Writer",
                    "fields": {
                        "action": {
                            "name": "Action",
                            "type": "Text",
                            "description": "What action to perform on the data (save, get, delete, list all keys).",
                            "options": {
                                "Save": "Save",
                                "Get": "Get",
                                "Delete": "Delete",
                                "List keys": "List keys",
                            },
                            "default": "Save",
                        },
                        "key": {
                            "name": "Key",
                            "type": "Text",
                            "description": "Unique identifier of your data that will be used to retrieve, update and delete it.",
                        },
                        "valueType": {
                            "name": "Value type",
                            "type": "Text",
                            "description": "Specify whether to interpret the value as plain text or JSON.",
                            "options": {
                                "text": "Plain text",
                                "JSON": "JSON",
                            },
                            "default": "text",
                        },
                        "value": {
                            "name": "Value",
                            "type": "Text",
                            "description": "Data that you want to store.",
                            "control": "Textarea",
                        },
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
        try:
            self.result = self._execute_action()
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e

    def _execute_action(self):
        from writer.journal import JOURNAL_KEY_PREFIX
        from writer.keyvalue_storage import KeyValueStorage

        action = self._get_field("action", default_field_value="Save")

        with self.acquire_httpx_client() as client:
            writer_kv_storage = KeyValueStorage(client=client)

            if action == "List keys":
                response = writer_kv_storage.get_data_keys()
                return [key for key in response if not key.startswith(JOURNAL_KEY_PREFIX)]

            key = self._get_field("key", required=True)
            if not ALLOWED_CHARS.fullmatch(key):
                raise WriterConfigurationError("Key can only contain alphanumeric characters, underscores and hyphens")

            if action == "Save":
                value_type = self._get_field("valueType")
                value = self._get_field("value", as_json=value_type == "JSON")
                return writer_kv_storage.save(key, value)
            if action == "Get":
                return writer_kv_storage.get(key, type_="data")["data"]
            if action == "Delete":
                return writer_kv_storage.delete(key)

            raise WriterConfigurationError(f"Unknown action for the Key-Value Storage: {action}")
