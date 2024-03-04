from typing import Optional
from streamsync.ui_manager import StreamsyncUI
from streamsync.ui_utils import Component


class StreamsyncUIManager(StreamsyncUI):
    """The StreamsyncUIManager class is intended to include dynamically-
    generated methods corresponding to UI components defined in the Vue
    frontend during the build process.

    This class serves as a bridge for programmatically interacting with the
    frontend, allowing methods to adapt to changes in the UI components without
    manual updates.
    """

    # Hardcoded classes for proof-of-concept purposes

    def ColumnContainer(self, **kwargs) -> Component:
        component_context = self.create_container('columns', **kwargs)
        return component_context

    def Column(self, **kwargs) -> Component:
        component_context = self.create_container('column', **kwargs)
        return component_context

    def Text(self, text: Optional[str] = None, **kwargs) -> Component:
        component = self.create_component('text', content={'text': text}, **kwargs)
        return component
