"""
This module manipulates the folder of a wf project stored into `wf`.

>>> wf_project.write_files('app/hello', metadata={"writer_version": "0.1" }, components=...)

>>> metadata, components = wf_project.read_files('app/hello')
"""
import io
import json
import logging
import os
import typing
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

from writer import core_ui
from writer.ss_types import ComponentDefinition, MetadataDefinition

ROOTS = ['root', 'workflows_root']
COMPONENT_ROOTS = ['page', 'workflows_workflow']

def write_files(app_path: str, metadata: MetadataDefinition, components: Dict[str, ComponentDefinition]) -> None:
    """
    Writes the meta data of the WF project to the `.wf` directory (metadata, components, ...).

    * the metadata.json file is written in json format
    * a file for the root component written in jsonline format
    * a file for the workflows_root component written in jsonline format
    * one file per page is created in the form `components-page-{id}.json` in jsonline format
    * one file per workflow is created in the form `components-workflows_workflow-{id}.json` in jsonline format

    >>> wf_project.write_files('app/hello', metadata={"writer_version": "0.1" }, components=...)
    """
    wf_directory = os.path.join(app_path, ".wf")
    if not os.path.exists(wf_directory):
        os.makedirs(wf_directory)

    with io.open(os.path.join(wf_directory, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    _write_root_files(wf_directory, components)
    _write_component_files(wf_directory, components)
    _remove_obsolete_component_files(wf_directory, components)


def read_files(app_path: str) -> Tuple[MetadataDefinition, dict[str, ComponentDefinition]]:
    """
    Reads project files in the `.wf` folder.

    The components are read in page and workflows_workflow order.

    >>> metadata, components = wf_project.read_files('app/hello')
    """
    components: dict[str, ComponentDefinition] = {}
    roots = ['root', 'workflows_root']
    component_part_file_type = ['page', 'workflows_workflow']

    meta_data_path = os.path.join(app_path, ".wf", "metadata.json")
    try:
        with io.open(meta_data_path, "r") as filep:
            metadata: MetadataDefinition = json.load(filep)
    except Exception as e:
        raise ValueError(f"Error reading metadata file {meta_data_path} : {e}")


    # read ui files
    for root in roots:
        root_component_path = os.path.join(app_path, ".wf", f"components-{root}.jsonl")
        if not os.path.exists(root_component_path):
            continue

        try:
            with io.open(root_component_path, "r") as filep:
                root_component: ComponentDefinition = json.loads(filep.read())
                components.update({root_component["id"]: root_component})
        except Exception as e:
            raise ValueError(f"Error reading root component file {root_component_path} : {e}")

    files = sorted(os.listdir(os.path.join(app_path, ".wf")))
    for file in files:
        for part_file_type in component_part_file_type:
            if file.startswith(f"components-{part_file_type}-"):
                page_file_path = os.path.join(app_path, ".wf", file)
                try:
                    with io.open(page_file_path, "r") as filep:
                        for line in filep:
                            component: ComponentDefinition = json.loads(line)
                            components.update({component["id"]: component})
                except Exception as e:
                    raise ValueError(f"Error reading page component file {page_file_path} : {e}")

    return metadata, components


def migrate_obsolete_ui_json(app_path: str) -> None:
    """
    Migrates a project that uses ui.json file to the current project format

    The ui.json file is removed after the migration.

    >>> wf_project.migrate_obsolete_ui_json('app/hello')
    """
    assert os.path.isfile(os.path.join(app_path, "ui.json")), f"ui.json file required for migration into {app_path}"

    logger = logging.getLogger('writer')
    with io.open(os.path.join(app_path, "ui.json"), "r") as f:
        parsed_file = json.load(f)

    if not isinstance(parsed_file, dict):
        raise ValueError("No dictionary found in components file.")

    file_payload = parsed_file
    metadata = file_payload.get("metadata", {})
    components = file_payload.get("components", {})
    write_files(app_path, metadata, components)
    os.remove(os.path.join(app_path, "ui.json"))
    logger.warning('project format has changed and has been migrated with success. ui.json file has been removed.')


def create_default_workflows_root(abs_path: str) -> None:
    with io.open(os.path.join(abs_path, '.wf', 'components-workflows_root.jsonl'), 'w') as f:
        f.write('{"id": "workflows_root", "type": "workflows_root", "content": {}, "isCodeManaged": false, "position": 0, "handlers": {}, "visible": {"expression": true, "binding": "", "reversed": false}}')
        logger = logging.getLogger('writer')
        logger.warning('project format has changed and has been migrated with success. components-workflows_root.jsonl has been added.')


def _expected_component_fileinfos(components: dict[str, ComponentDefinition]) -> List[Tuple[str, str]]:
    """
    Returns the list of component file information to write (id, filename).

    >>> component_files = expected_component_files(components)
    >>> for component_id, filename in component_files:
    >>>     print(f"Components that depends on {component_id} will be written in {filename}")
    """
    expected_component_files = []
    for component_file_root in COMPONENT_ROOTS:
        position = 0
        for c in components.values():
            if c["type"] == component_file_root:
                filename = f"components-{ component_file_root }-{position}-{c['id']}.jsonl"
                expected_component_files.append((c["id"], filename))
                position += 1

    return expected_component_files


def _list_component_files(wf_directory: str) -> List[str]:
    """
    List the component files of the .wf folder.

    The component files are of the form `components-{type}-....jsonl`
    """
    patterns = [f"components-{cr}-" for cr in COMPONENT_ROOTS]
    return [f for f in os.listdir(wf_directory) if any(p in f for p in patterns)]


def _remove_obsolete_component_files(wf_directory: str, components: Dict[str, ComponentDefinition]):
    """
    Remove the obsolete component files in the .wf folder.
    """
    expected_component_files = {f for cid, f in _expected_component_fileinfos(components)}
    list_component_files = set(_list_component_files(wf_directory))

    obsolete_components_files = list_component_files - expected_component_files
    for f in obsolete_components_files:
        os.remove(os.path.join(wf_directory, f))


def _sort_wf_component_keys(obj: typing.Union[ComponentDefinition, dict]) -> Any:
    """
    Sorts the keys of the object recursively to have a consistent order in the json file.

    Id and type attributes first, then use alphabetical order.
    """
    if not isinstance(obj, dict):
        return obj

    def sort_key(item):
        return item[0].replace("id", "0_id").replace("type", "1_type")

    sorted_items = sorted(obj.items(), key=sort_key)
    return OrderedDict((k, _sort_wf_component_keys(v)) for k, v in sorted_items)


def _write_component_files(wf_directory: str, components: Dict[str, ComponentDefinition]) -> None:
    """
    Writes the component files in the .wf folder. It preserve obsolete files.

    The components are written in the form `components-{type}-{position}-{id}.jsonl`
    """
    for component_id, filename in _expected_component_fileinfos(components):
        filtered_components = core_ui.filter_components_by(components, parent=component_id)

        with io.open(os.path.join(wf_directory, filename), "w") as f:
            for p in _order_components(filtered_components):
                f.write(json.dumps(_sort_wf_component_keys(p)) + "\n")


def _write_root_files(wf_directory, components):
    for root in ROOTS:
        root_component = components.get(root, None)
        if root_component:
            with io.open(os.path.join(wf_directory, f"components-{root}.jsonl"), "w") as f:
                f.write(json.dumps(_sort_wf_component_keys(root_component)))


def _order_components(components: Dict[str, ComponentDefinition]) -> List[ComponentDefinition]:
    """
    Orders the components by their position attribute

    >>> ordered_components = _order_components(components)
    """

    def _hierarchical_position(components, c):
        p = [c['position']]
        while c['parentId'] is not None and c['parentId'] in components:
            c = components[c['parentId']]
            p.append(c['position'])

        return list(reversed(p))

    return sorted(components.values(), key=lambda c: _hierarchical_position(components, c))

