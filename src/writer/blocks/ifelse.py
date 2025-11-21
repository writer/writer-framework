from typing import Any

from writer.abstract import register_abstract_template
from writer.blocks import CodeBlock
from writer.ss_types import AbstractTemplate

INIT_CODE = """import random
# Pass a boolean value to `set_outcome` to trigger the "True" or "False" branch
set_outcome(random.random() > 0.5)

# State is accessible as a global variable. For example:
# state["counter"] = 10

# Other variables from the execution environment are also available. For example:
# result # Result from the execution of the last block
# results # Dictionary with the execution results of each block, with the block id as key
# payload # When executing via API or via an UI event with a payload
# logger # logging.Logger object for capturing logs

# To set the output of this block, which will be available via result to the next block:
"""


class IfElseBlock(CodeBlock):
    @classmethod
    def register(cls, type: str):
        super(IfElseBlock, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "If-Else",
                    "description": "Evaluate custom Python code and redict to 'true' or 'false' branch. Useful for conditionnal logic.",
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
                        "true": {
                            "name": "True",
                            "description": "The event handler execution for True.",
                            "style": "success",
                        },
                        "false": {
                            "name": "False",
                            "description": "The event handler execution for False.",
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

    def set_outcome(self, output: Any):
        if bool(output):
            self.if_outcome = "true"
        else:
            self.if_outcome = "false"

    def _get_block_global_functions(self):
        funcs = super()._get_block_global_functions()
        funcs["set_outcome"] = self.set_outcome
        return funcs

    def run(self):
        super().run()
        if self.outcome != "error":
            self.outcome = self.if_outcome
