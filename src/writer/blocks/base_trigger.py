from writer.blocks.base_block import BlueprintBlock
from writer.ss_types import WriterConfigurationError


class BlueprintTrigger(BlueprintBlock):
    def run(self):
        self.result = self.execution_environment.get("payload")

        if not self.result:
            try:
                self.result = self._get_field("defaultResult", True, None)
            except WriterConfigurationError:
                self.result = self._get_field("defaultResult", False, None)

