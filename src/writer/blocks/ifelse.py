import sys
import traceback

from writer.abstract import register_abstract_template
from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import AbstractTemplate


class IfElseBlock(BlueprintBlock):
    @classmethod
    def register(cls, type: str):
        super(IfElseBlock, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "If-Else",
                    "description": "Evaluate custom Python code and redirect to 'true' or 'false' branch. Useful for conditional logic.",
                    "category": "Logic",
                    "fields": {
                        "expression": {
                            "name": "Expression",
                            "type": "Eval",
                            "desc": "The expression to be evaluated. Must be a single expression (no statements).",
                            "init": 'state["counter"] > 10',
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
                            "description": "The expression evaluation failed.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def run(self):
        expression = self._get_field("expression")

        try:
            writeruserapp = sys.modules.get("writeruserapp")
            block_globals = {
                **self.execution_environment,
                **(writeruserapp.__dict__ if writeruserapp else {}),
                "state": self.runner.session.session_state,
            }
            # Evaluate the expression and set the result
            compiled_expr = compile(expression, "<expression>", mode="eval")
            self.result = eval(compiled_expr, block_globals)

            if self.result:
                self.outcome = "true"
            else:
                self.outcome = "false"
        except BaseException:
            self.outcome = "error"
            self.message = f"<pre>{traceback.format_exc()}</pre>"
            raise
