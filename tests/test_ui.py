from streamsync.core_ui import ComponentTree, UIError
from streamsync.ui import StreamsyncUIManager
import streamsync as ss

import json

from tests import test_app_dir

sc = None
with open(test_app_dir / "ui.json", "r") as f:
    sc = json.load(f).get("components")
session = ss.session_manager.get_new_session()
session.session_component_tree.ingest(sc)


class TestComponentTree:

    ct = ComponentTree()

    def test_ingest(self) -> None:
        self.ct.ingest(sc)
        d = self.ct.to_dict()
        assert d.get(
            "84378aea-b64c-49a3-9539-f854532279ee").get("type") == "header"

    def test_descendents(self) -> None:
        desc = self.ct.get_descendents("root")
        desc_ids = list(map(lambda x: x.id, desc))
        assert "84378aea-b64c-49a3-9539-f854532279ee" in desc_ids
        assert "bb4d0e86-619e-4367-a180-be28ab6059f4" in desc_ids
        assert "85120b55-69c6-4b50-853a-bbbf73ff8121" in desc_ids


class TestUIManager:
    ui_manager = StreamsyncUIManager(session.session_id)

    def test_find_component(self):
        # Verify that the find method correctly retrieves a component by its ID
        expected_id = "84378aea-b64c-49a3-9539-f854532279ee"
        found_component = self.ui_manager.find(expected_id)
        assert found_component is not None
        assert found_component.id == expected_id

    def test_assert_in_container_context(self):
        # Verify the context assertion for creating components within a container
        # First, successfully create a component within a container context
        with self.ui_manager.root:
            passed = False
            try:
                self.ui_manager.create_component('text', content={'text': 'Inside container'})
                passed = True
            except Exception:
                passed = False
            assert passed, "Component should be created within container context without errors"

        # Now, attempt to create a component outside of any container context, which should raise an error
        raised = False
        try:
            self.ui_manager.create_component('text', content={'text': 'Outside container'})
        except UIError:
            raised = True
        assert raised, "Creating a component outside of a container context should raise an UIError"

    def test_column_container_creation(self):
        container = self.ui_manager.ColumnContainer(id="test_container")
        assert container.type == 'columns'
        assert container.id == "test_container"
        assert container in self.ui_manager.session.session_component_tree.components.values()

    def test_column_container_creation_no_id(self):
        container = self.ui_manager.ColumnContainer()
        assert container.type == 'columns'
        assert container.id is not None
        assert container in self.ui_manager.session.session_component_tree.components.values()
        assert container.id in self.ui_manager.session.session_component_tree.components.keys()

    def test_column_creation(self):
        column = self.ui_manager.Column(id="test_column")
        assert column.type == 'column'
        assert column.id == "test_column"
        assert column in self.ui_manager.session.session_component_tree.components.values()

    def test_text_creation(self):
        with self.ui_manager.root:
            text_content = "Hello World"
            text_component = self.ui_manager.Text(text=text_content, id="test_text")
        assert text_component.type == 'text'
        assert text_component.content == {'text': text_content}
        assert text_component.id == "test_text"
        assert text_component.parentId == "root"
        assert text_component in self.ui_manager.session.session_component_tree.components.values()
