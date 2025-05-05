import io
import os
import shutil
import tempfile
from typing import List
from unittest.mock import ANY

from writer import VERSION, core_ui, wf_project
from writer.ss_types import ComponentDefinition

from tests.backend import test_app_dir
from tests.backend.fixtures import file_fixtures, load_fixture_content


def test_wf_project_write_files_should_write_metadatajson_in_wf_directory():
    """
    Tests that the function writes the meta information to the .wf configuration folder
    with a metadata.json file and a file for the root and a file per page.

    """
    with tempfile.TemporaryDirectory('test_wf_project_write_files') as test_app_dir:
        # Given
        components_root: List[ComponentDefinition] = load_fixture_content('components/components-root.jsonl')
        components = {c['id']: c for c in components_root}

        # When
        wf_project.write_files(
            test_app_dir,
            metadata={'writer_version': '0.1.0'},
            components=components,
            context=wf_project.WfProjectContext(app_path=test_app_dir)
        )

        # Then
        assert os.path.isfile(os.path.join(test_app_dir, '.wf', 'metadata.json'))
        metadata: dict = file_fixtures.read(os.path.join(test_app_dir, '.wf', 'metadata.json'))
        assert metadata['writer_version'] == '0.1.0'

def test_wf_project_write_files_should_write_components_files_in_wf_directory():
    """
    Tests that the wf_project_write_files function writes the `components-.jsonl` files to the `.wf` directory

    * the components-root.jsonl file is written
    * the components-page-0-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl file is written
    """
    with tempfile.TemporaryDirectory('test_wf_project_write_files') as test_app_dir:
        # Given
        components_root: List[ComponentDefinition] = load_fixture_content('components/components-root.jsonl')
        components = {c['id']: c for c in components_root }

        component_page: List[ComponentDefinition] = load_fixture_content('components/components-page-0.jsonl')
        components.update({c['id']: c for c in component_page})

        # When
        wf_project.write_files(
            test_app_dir,
            metadata={'writer_version': '0.1.0'},
            components=components,
            context=wf_project.WfProjectContext(app_path=test_app_dir)
        )

        # Then
        assert os.path.isfile(os.path.join(test_app_dir, '.wf', 'components-root.jsonl'))
        root: List[ComponentDefinition] = file_fixtures.read(os.path.join(test_app_dir, '.wf', 'components-root.jsonl'))
        assert root[0] == components_root[0]

        assert os.path.isfile(os.path.join(test_app_dir, '.wf', 'components-page-0-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl'))
        page: List[ComponentDefinition] = file_fixtures.read(os.path.join(test_app_dir, '.wf', 'components-page-0-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl'))
        assert page[0] == component_page[0]

def test_wf_project_write_files_should_write_preserve_page_order_in_wf_directory():
    """
    Tests that wf_project_write_files preserves the order of pages defined in the component structure

    * the components of `components-page-1.jsonl` loaded first are written to the file `components-page-0-23bc1387-26ed-4ff2-8565-b027c2960c3c.jsonl`
    * the components of `components-page-0.jsonl` loaded second are written in the file `components-page-1-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl`

    """
    with tempfile.TemporaryDirectory('test_wf_project_write_files') as test_app_dir:
        # Given
        components_root: List[ComponentDefinition] = load_fixture_content('components/components-root.jsonl')
        components = {c['id']: c for c in components_root }

        components_page_0: List[ComponentDefinition] = load_fixture_content('components/components-page-1.jsonl')
        components.update({c['id']: c for c in components_page_0})

        components_page_1: List[ComponentDefinition] = load_fixture_content('components/components-page-0.jsonl')
        components.update({c['id']: c for c in components_page_1})

        # When
        wf_project.write_files(
            test_app_dir,
            metadata={'writer_version': '0.1.0'},
            components=components,
            context=wf_project.WfProjectContext(app_path=test_app_dir)
        )

        # Then
        assert os.path.isfile(os.path.join(test_app_dir, '.wf', 'components-page-0-23bc1387-26ed-4ff2-8565-b027c2960c3c.jsonl'))
        page_0: List[ComponentDefinition] = file_fixtures.read(os.path.join(test_app_dir, '.wf', 'components-page-0-23bc1387-26ed-4ff2-8565-b027c2960c3c.jsonl'))
        assert page_0[0] == components_page_0[0]

        assert os.path.isfile(os.path.join(test_app_dir, '.wf', 'components-page-1-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl'))
        page_1: List[ComponentDefinition] = file_fixtures.read(os.path.join(test_app_dir, '.wf', 'components-page-1-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl'))
        assert page_1[0] == components_page_1[0]


def test_wf_project_write_files_updates_context():
    """
    Tests that files with the same hash do not get rewritten
    """
    # Given
    components_root: List = load_fixture_content('components/components-root.jsonl')
    components = {c['id']: c for c in components_root if "hash" not in c}

    components_page: List = load_fixture_content('components/components-page-0.jsonl')
    components.update({c['id']: c for c in components_page if "hash" not in c})

    with tempfile.TemporaryDirectory('test_wf_project_write_files') as temp_test_app_dir:
        # When
        context = wf_project.WfProjectContext(app_path=temp_test_app_dir)
        wf_project.write_files(
            temp_test_app_dir,
            metadata={'writer_version': '0.1.0'},
            components=components,
            context=context
        )

        # Then
        assert context.file_hashes == {
            'components-page-0-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl': '7416851a26306bb3a62fac797e7f6f60',
            'components-root.jsonl': '14255037a5c472eca4e0ff8308e2efbb',
        }


def test_wf_project_read_files_should_read_files_in_wf_directory():
    # When
    metadata, sc = wf_project.read_files(test_app_dir)

    # Then
    assert 'writer_version' in metadata
    assert isinstance(sc, dict)
    assert len(sc) != 0


def test_wf_project_should_remove_obsolete_pages_in_wf_directory():
    # When
    with tempfile.TemporaryDirectory('test_wf_project_write_files') as _test_app_dir:
        shutil.copytree(test_app_dir, _test_app_dir, dirs_exist_ok=True)
        assert os.path.isfile(os.path.join(test_app_dir, '.wf', 'components-page-0-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl')) is True
        metadata, sc = wf_project.read_files(test_app_dir)

        removed_components = core_ui.filter_components_by(sc, 'bb4d0e86-619e-4367-a180-be28ab6059f4')
        for rc in removed_components.values():
            del sc[rc['id']]

        wf_project.write_files(
            _test_app_dir,
            metadata={'writer_version': '0.1.0'},
            components=sc,
            context=wf_project.WfProjectContext(app_path=_test_app_dir)
        )

        # Then
        assert os.path.isfile(os.path.join(_test_app_dir, '.wf', 'components-page-0-bb4d0e86-619e-4367-a180-be28ab6059f4.jsonl')) is False


def test_wf_project_can_create_project_does_not_work_on_project_with_a_directory():
    with tempfile.TemporaryDirectory('test_wf_project_can_create_project') as tmp_app_dir:
        io.open(os.path.join(tmp_app_dir, 'file'), 'w').close()

        # When
        is_wf_project = wf_project.is_project(tmp_app_dir)
        can_create_wf_project = wf_project.can_create_project(tmp_app_dir)

        # Then
        assert is_wf_project is False
        assert can_create_wf_project is False


def test_wf_project_can_create_project_on_empty_directory():
    with tempfile.TemporaryDirectory('test_wf_project_can_create_project') as tmp_app_dir:
        # When
        is_wf_project = wf_project.is_project(tmp_app_dir)
        can_create_wf_project = wf_project.can_create_project(tmp_app_dir)

        # Then
        assert is_wf_project is False
        assert can_create_wf_project is True
