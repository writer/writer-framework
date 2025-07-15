import io
import logging
import sys
import traceback
from typing import Any

from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.logs import use_logging_redirect, use_stdout_redirect
from writer.ss_types import AbstractTemplate

exec_logger = logging.getLogger("exec_logger")

INIT_CODE = """
# State is accessible as a global variable. For example:
state["counter"] = 10

# Other variables from the execution environment are also available. For example:
result # Result from the execution of the last block
results # Dictionary with the execution results of each block, with the block id as key
payload # When executing via API or via an UI event with a payload
logger # logging.Logger object for capturing logs

# To set the output of this block, which will be available via result to the next block:
set_output("a sample result")

"""


class CodeBlock(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        super(CodeBlock, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Python code",
                    "description": "Runs custom Python code. Useful for logic not covered by existing blocks.",
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

    def set_output(self, output: Any):
        self.result = output

    def run(self):
        try:
            code = self._get_field("code")
            self.result = None

            writeruserapp = sys.modules.get("writeruserapp")
            block_globals = (
                {
                    "state": self.runner.session.session_state,
                }
                | self.execution_environment
                | writeruserapp.__dict__
                | {"set_output": self.set_output}
            )

            with (
                use_stdout_redirect(lambda entry: self.runner.session.session_state.add_log_entry("info", "Captured stdout", entry)),
                use_logging_redirect(lambda entry: self.runner.session.session_state.add_log_entry("info", "Captured logs", entry)),
            ):
                exec(code, block_globals | {"logger": exec_logger})

            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            # Wrap the message as a preformatted block to display as "raw" text in Markdown
            self.message = f"<pre>{traceback.format_exc()}</pre>"
            raise e
