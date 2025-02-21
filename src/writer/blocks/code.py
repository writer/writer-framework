import io
import sys

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate

INIT_CODE = """# State is accessible as a global variable. For example:
state["counter"] = 10

# Other variables from the execution environment are also available. For example:
result # Result from the execution of the last block
results # Dictionary with the execution results of each block, with the block id as key
payload # When executing via API or via an UI event with a payload"""


class CodeBlock(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(CodeBlock, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="workflows_node",
                writer={
                    "name": "Python code",
                    "description": "Executes Python code.",
                    "category": "Logic",
                    "fields": {
                        "code": {
                            "name": "Code",
                            "type": "Code",
                            "control": "Textarea",
                            "desc": "The code to be executed.",
                            "init": INIT_CODE,
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
            code = self._get_field("code")

            output_buffer = io.StringIO()
            sys.stdout = output_buffer

            writeruserapp = sys.modules.get("writeruserapp")

            exec(
                code,
                {
                    "state": self.runner.session.session_state,
                }
                | self.execution_environment
                | writeruserapp.__dict__,
            )

            sys.stdout = sys.__stdout__
            captured_output = output_buffer.getvalue()

            self.result = captured_output
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
