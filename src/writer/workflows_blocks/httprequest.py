import requests

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class HTTPRequest(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(HTTPRequest, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "HTTP Request",
                "description": "Executes an HTTP request.",
                "category": "Content",
                "fields": {
                    "method": {
                        "name": "Method",
                        "type": "Text",
                        "options": {
                            "get": "GET",
                            "post": "POST",
                            "put": "PUT",
                            "patch": "PATCH",
                            "delete": "DELETE"
                        },
                        "default": "get"
                    },
                    "url": {
                        "name": "URL",
                        "type": "Text",
                    },
                    "headers": {
                        "name": "Headers",
                        "type": "Key-Value",
                        "default": "{}",
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
                        "description": "The connection was established successfully but an error response code was received.",
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

    def run(self):
        try:
            method = self._get_field("method", False, "get")
            url = self._get_field("url")
            headers = self._get_field("headers")
            body = self._get_field("body")
            req = requests.request(method, url, headers=headers, data=body)
            self.result = req.text
            if req.ok:
                self.outcome = "success"
            else:
                self.outcome = "responseError"
        except BaseException as e:
            self.outcome = "connectionError"
            raise e