import json

from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate


class HTTPRequest(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        super(HTTPRequest, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "HTTP Request",
                    "description": "Sends a HTTP request to an API endpoint. Used to fetch data or send data.",
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
                                "DELETE": "DELETE",
                            },
                            "default": "GET",
                            "validator": {
                                "type": "string",
                                "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                            },
                        },
                        "url": {
                            "name": "URL",
                            "type": "Text",
                            "control": "Textarea",
                            "validator": {
                                "type": "string",
                                "format": "uri",
                            },
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
                            },
                        },
                        "bodyType": {
                            "name": "Body type",
                            "type": "Text",
                            "description": "Specify whether to interpret the body as plain text or JSON.",
                            "options": {
                                "text": "Plain text",
                                "JSON": "JSON",
                            },
                            "default": "text",
                        },
                        "body": {"name": "Body", "type": "Text", "control": "Textarea"},
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
                },
            ),
        )

    def run(self):
        try:
            method = self._get_field("method", False, "GET")
            url = self._get_field("url")
            headers = self._get_field(
                "headers", True, default_field_value="{}"
                )
            body_type = self._get_field("bodyType")
            body = None
            raw_body = None

            if body_type == "JSON":
                body = self._get_field("body", as_json=True)
                raw_body = json.dumps(body)
                headers.setdefault("Content-Type", "application/json")
            else:
                body = self._get_field("body", as_json=False)
                raw_body = body

            with self.acquire_httpx_client() as client:
                res = client.request(
                    method,
                    url,
                    headers=headers,
                    content=raw_body,
                    timeout=180
                    )

                content_type = res.headers.get("Content-Type", "")
                is_response_json = "application/json" in content_type

                self.result = {
                    "request": {
                        "url": str(res.request.url),
                        "headers": dict(res.request.headers),
                        "body": res.request.content.decode(
                            "utf-8", errors="replace"
                            ),
                    },
                    "headers": dict(res.headers),
                    "status_code": res.status_code,
                    "body": res.json() if is_response_json else res.text,
                }

                if res.is_success:
                    self.outcome = "success"
                else:
                    self.outcome = "responseError"
                    raise RuntimeError(
                        f"HTTP response with code {res.status_code}"
                        f" and message {res.text}"
                        )

        except json.JSONDecodeError as e:
            self.outcome = "responseError"
            raise e
        except Exception as e:
            if self.outcome is None or self.outcome not in ("responseError",):
                self.outcome = "connectionError"
            raise e
