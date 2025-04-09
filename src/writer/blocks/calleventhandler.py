import inspect

import writer.core
from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate


class CallEventHandler(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        super(CallEventHandler, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Call event handler",
                    "description": "Executes an event handler.",
                    "category": "Logic",
                    "deprecated": True,
                    "fields": {
                        "name": {
                            "name": "Name",
                            "type": "Handler",
                            "desc": "The name of the event handling function.",
                        },
                        "additionalArgs": {
                            "name": "Additional arguments",
                            "init": '{ "my_arg": 2 }',
                            "type": "Object",
                            "control": "Textarea",
                            "default": "{}",
                        },
                    },
                    "outs": {
                        "success": {
                            "name": "Success",
                            "description": "The event handler execution was successful.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "The event handler execution wasn't successful.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        try:
            handler_name = self._get_field("name")
            additional_args = self._get_field("additionalArgs", as_json=True)

            current_app_process = writer.core.get_app_process()
            handler_registry = current_app_process.handler_registry
            callable_handler = handler_registry.find_handler_callable(handler_name)

            args = {
                "state": self.runner.session.session_state,
                "context": self.execution_environment,
                "session": writer.core._event_handler_session_info(),
                "ui": writer.core._event_handler_ui_manager(),
            } | additional_args

            handler_args = inspect.getfullargspec(callable_handler).args
            func_args = []
            for arg in handler_args:
                if arg in args:
                    func_args.append(args[arg])
            self.result = callable_handler(*func_args)
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
