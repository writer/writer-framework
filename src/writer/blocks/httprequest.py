import re

import requests

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class HTTPRequest(WorkflowBlock):

    CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")

    @classmethod
    def register(cls, type: str):
        super(HTTPRequest, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "HTTP Request",
                "description": "Executes an HTTP request.",
                "category": "Other",
                "fields": {
                    "method": {
                        "name": "Method",
                        "type": "Text",
                        "options": {
                            "GET": "GET",
                            "POST": "POST",
                            "PUT": "PUT",
                            "PATCH": "PATCH",
                            "DELETE": "DELETE"
                        },
                        "default": "GET",
                        "validator": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                        }
                    },
                    "url": {
                        "name": "URL",
                        "type": "Text",
                        "validator": {
                            "type": "string",
                            "format": "uri",
                        }
                    },
                    "headers": {
                        "name": "Headers",
                        "type": "Key-Value",
                        "default": "{}",
                        "validator": {
                            "type": "object",
                            "patternProperties": {
                                "^.*$": {
                                    "type": ["string", "number", "boolean"],
                                },
                            },
                            "additionalProperties": True,
                        }
                    },
                    "body": {
                        "name": "Body",
                        "type": "Text",
                        "control": "Textarea"
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The request was successful.",
                        "style": "success",
                    },
                    "responseError": {
                        "name": "Response error",
                        "description": "The connection was established successfully but an error response code was received or the response was invalid.",
                        "style": "error",
                    },
                    "connectionError": {
                        "name": "Connection error",
                        "description": "The connection couldn't be established.",
                        "style": "error",
                    },
                },
            }
        ))

    def _clean_json_string(self, s: str) -> str:

        """ Remove control characters, which aren't tolerated by JSON loads() strict mode, from string."""

        return HTTPRequest.CONTROL_CHARS.sub("", s)

    def run(self):
        import json

        try:
            method = self._get_field("method", False, "GET")
            url = self._get_field("url")
            headers = self._get_field("headers", True)
            body = self._clean_json_string(self._get_field("body"))
            req = requests.request(method, url, headers=headers, data=body)
            
            content_type = req.headers.get("Content-Type")
            is_json = content_type and "application/json" in content_type
            
            self.result = {
                "headers": dict(req.headers),
                "status_code": req.status_code,
                "body": req.json() if is_json else req.text
            }
            if req.ok:
                self.outcome = "success"
            else:
                self.outcome = "responseError"
                raise RuntimeError("HTTP response with code " + str(req.status_code))
        except json.JSONDecodeError as e:
            self.outcome = "responseError"
            raise e
        except BaseException as e:
            if not self.outcome:
                self.outcome = "connectionError"
            raise e