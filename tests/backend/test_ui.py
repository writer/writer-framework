import contextlib
import json

import writer as wf
from writer import audit_and_fix, core, wf_project
from writer.core_ui import (
    Component,
    UIError,
    cmc_components_list,
    ingest_bmc_component_tree,
    session_components_list,
    use_component_tree,
)
from writer.ui import WriterUIManager

from backend.fixtures import core_ui_fixtures
from tests.backend import test_app_dir

_, sc = wf_project.read_files(test_app_dir)
sc = audit_and_fix.fix_components(sc)

@contextlib.contextmanager
def use_ui_manager_with_init_ui():
    """
    create a UIManager such that Framework retrieves it when an
    application loads in the `wf.init_ui` context.
    """
    core.reset_base_component_tree()
    ingest_bmc_component_tree(core.base_component_tree, sc)
    with use_component_tree(core.base_component_tree):
        yield WriterUIManager()


@contextlib.contextmanager
def use_ui_manager_with_event_handler():
    """
    create a UIManager such that Framework retrieves it in
    an event handler context.
    """
    core.reset_base_component_tree()
    ingest_bmc_component_tree(core.base_component_tree, sc)
    session = wf.session_manager.get_new_session()
    with use_component_tree(session.session_component_tree):
        yield WriterUIManager()


class TestComponentTree:

    def test_ingest(self) -> None:
        with use_ui_manager_with_init_ui() as ui:
            d = ui.component_tree.to_dict()
            assert d.get(
                "84378aea-b64c-49a3-9539-f854532279ee").get("type") == "header"

    def test_descendents(self) -> None:
        with use_ui_manager_with_init_ui() as ui:
            desc = ui.component_tree.get_descendents("root")
            desc_ids = [x.id for x in desc]
            assert "84378aea-b64c-49a3-9539-f854532279ee" in desc_ids
            assert "bb4d0e86-619e-4367-a180-be28ab6059f4" in desc_ids
            assert "85120b55-69c6-4b50-853a-bbbf73ff8121" in desc_ids


class TestUIManager:

    def test_find_component(self):
        with use_ui_manager_with_init_ui() as ui:
            # Verify that the find method correctly retrieves a component by its ID
            expected_id = "84378aea-b64c-49a3-9539-f854532279ee"
            with ui.find(expected_id) as found_component:
                assert found_component is not None
                assert found_component.id == expected_id

    def test_find_component_no_context(self):
        with use_ui_manager_with_init_ui() as ui:
            # Verify that the find method correctly retrieves a component by its ID
            expected_id = "84378aea-b64c-49a3-9539-f854532279ee"
            found_component = ui.find(expected_id)
            assert found_component is not None
            assert found_component.id == expected_id

    def test_assert_in_container_context(self):
        # Verify the context assertion for creating components within a container
        # First, successfully create a component within a container context
        with use_ui_manager_with_init_ui() as ui:
            with ui.root:
                passed = False
                try:
                    ui.create_component('text', text='Inside container')
                    passed = True
                except Exception:
                    passed = False
                assert passed, "Component should be created within container context without errors"

            # Now, attempt to create a component outside of any container context, which should raise an error
            raised = False
            try:
                ui.create_component('text', text='Outside container')
            except UIError:
                raised = True
            assert raised, "Creating a component outside of a container context should raise an UIError"

    def test_column_container_creation(self):
        with use_ui_manager_with_init_ui() as ui:
            with ui.ColumnContainer(id="test_container") as container:
                assert container.type == 'columns'
                assert container.id == "test_container"
                assert container in ui.component_tree.components.values() # visible in component list
                assert container in cmc_components_list(ui.component_tree) # present in the cmc component fragment

    def test_column_container_creation_no_context(self):
        with use_ui_manager_with_init_ui() as ui:
            container = ui.ColumnContainer(id="test_container")
            assert container.type == 'columns'
            assert container.id == "test_container"
            assert container in ui.component_tree.components.values()  # visible in component list
            assert container in cmc_components_list(ui.component_tree)  # present in the cmc component fragment

    def test_column_container_creation_no_id(self):
        with use_ui_manager_with_init_ui() as ui:
            with ui.ColumnContainer() as container:
                assert container.type == 'columns'
                assert container.id is not None
                assert container in ui.component_tree.components.values()
                assert container.id in ui.component_tree.components.keys()

    def test_column_creation(self):
        with use_ui_manager_with_init_ui() as ui:
            with ui.Column(id="test_column") as column:
                assert column.type == 'column'
                assert column.id == "test_column"
                assert column in ui.component_tree.components.values()

    def test_text_creation(self):
        with use_ui_manager_with_init_ui() as ui:
            with ui.Column(id="test_column") as column:
                text_content = "Hello World"
                text_component = ui.Text({"text": text_content}, id="test_text")
            assert text_component.type == 'text'
            assert text_component.content.get("text") == text_content
            assert text_component.id == "test_text"
            assert text_component.parentId == column.id
            assert text_component in ui.component_tree.components.values()
            assert text_component in cmc_components_list(ui.component_tree)  # present in the cmc component fragment


    def test_parent_should_return_the_first_level_parent(self):
        """
        Test that the parent method returns the first level parent of a component
        """
        # Given
        fake_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id='test_button', parentId='root', type='button'),
        ], init_root=True)

        with use_component_tree(fake_component_tree):
            # When
            id = WriterUIManager().parent('test_button', 1)

            # Then
            assert id == 'root'

    def test_parent_should_return_the_2_level_parent(self):
        """
        Test that the parent with level 2 as argument returns the 2 level parent of a component
        """
        # Given
        fake_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id='section1', parentId='root', type='section'),
            Component(id='section2', parentId='section1', type='section'),
            Component(id='test_button', parentId='section2', type='button'),
            Component(id='section3', parentId='root', type='section'),
        ], init_root=True)

        with use_component_tree(fake_component_tree):
            # When
            id = WriterUIManager().parent('test_button', 2)
            # Then
            assert id == 'section1'


    def test_text_creation_should_create_component_in_session_when_triggered_on_event_handler(self):
        with use_ui_manager_with_event_handler() as ui:
            with ui.Column(id="test_column"):
                text_component = ui.Text({"text": "Hello World"})

            assert text_component in ui.component_tree.components.values()
            assert text_component in session_components_list(ui.component_tree)  # present in the session component fragment
            assert text_component not in cmc_components_list(ui.component_tree)

    def test_update_bmc_component_tree_should_not_work_from_event_handlers(self):
        with use_ui_manager_with_event_handler() as ui:
            try:
                ingest_bmc_component_tree(ui.component_tree, sc)
            except AssertionError as exception:
                assert str(exception) == "builder managed component tree are frozen and cannot be updated"

    def test_refresh_with_should_remove_existing_children(self):
        """
        Verifies that context refresh with cleans up existing children of the specified component
        """
        # Given
        fake_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id='section1', parentId='root', type='section'),
            Component(id='section2', parentId='section1', type='section'),
            Component(id='test_button', parentId='section2', type='button'),
            Component(id='section3', parentId='root', type='section'),
        ], init_root=True)


        with use_component_tree(fake_component_tree):
            ui = WriterUIManager()

            assert len(ui.component_tree.components) == 5

            # When
            with ui.refresh_with('section1'):
                ui.Text({"text": "New content"}, id="new-content-1")

            # Then
            assert len(ui.component_tree.components) == 4

    def test_refresh_with_should_remove_new_children(self):
        """
        Verifies that context refresh with cleans up existing children of the specified component
        """
        # Given
        fake_component_tree = core_ui_fixtures.build_fake_component_tree([
            Component(id='section1', parentId='root', type='section'),
            Component(id='section2', parentId='section1', type='section'),
            Component(id='test_button', parentId='section2', type='button'),
            Component(id='section3', parentId='root', type='section'),
        ], init_root=True)


        with use_component_tree(fake_component_tree):
            ui = WriterUIManager()

            with ui.refresh_with('section1'):
                ui.Text({"text": "New content"}, id="new-content-1")

            assert len(ui.component_tree.components) == 4

            with ui.refresh_with('section1'):
                assert len(ui.component_tree.components) == 3
