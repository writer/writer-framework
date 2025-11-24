"""
Custom block implementation for user-created blocks.

Custom blocks execute user-provided Python code in the same execution
environment as CodeBlock (state, payload, result, results, set_output, logger).
"""

from typing import TYPE_CHECKING, Dict

import writer.core_ui
from writer.blocks.code import CodeBlock
from writer.blocks.custom_block_registry import get_block_code

if TYPE_CHECKING:
    from writer.blueprints import BlueprintRunner


class CustomBlock(CodeBlock):
    """
    Custom block that executes user-provided Python code.

    The code is loaded from the block registry based on the block type.
    """

    def __init__(
        self,
        component: writer.core_ui.Component,
        runner: "BlueprintRunner",
        execution_environment: Dict,
    ):
        super().__init__(component, runner, execution_environment)
        self.block_code = get_block_code(component.type)

    def run(self):
        """Execute the custom block code."""
        if not self.block_code:
            raise ValueError(f"No code found for block type: {self.component.type}")

        try:
            self._execute_code(self.block_code)
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            import traceback
            self.message = f"<pre>{traceback.format_exc()}</pre>"
            raise e

