"""
This module manipulates the folder of a wf project stored into `wf`.

>>> wf_project.write_files('app/hello', metadata={"writer_version": "0.1" }, components=...)

>>> metadata, components = wf_project.read_files('app/hello')
"""
import io
import json
import logging
import os
from typing import Tuple

from writer import core_ui
from writer.ss_types import ComponentDefinition, MetadataDefinition


def write_files(app_path: str, metadata: MetadataDefinition, components: dict[str, ComponentDefinition]) -> None:
    """
    Writes the meta data of the WF project to the `.wf` directory (metadata, components, ...).

    * the metadata.json file is written in json format
    * a file for the root component written in jsonline format
    * one file per page is created in the form `components-{id}.json` in jsonline format

    >>> wf_project.write_files('app/hello', metadata={"writer_version": "0.1" }, components=...)
    """
    wf_directory = os.path.join(app_path, ".wf")
    if not os.path.exists(wf_directory):
        os.makedirs(wf_directory)

    with io.open(os.path.join(wf_directory, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    root_component = components["root"]
    with io.open(os.path.join(wf_directory, "components-root.jsonl"), "w") as f:
        f.write(json.dumps(root_component))

    list_pages = []
    for c in components.values():
        if c["type"] == "page":
            list_pages.append(c["id"])

    for position, page_id in enumerate(list_pages):
        page_components = []
        page_components_ids = {page_id}
        for c in components.values():
            if core_ui.lookup_page_for_component(components, c['id']) in page_components_ids:
                page_components.append(c)
                page_components_ids.add(c["id"])

        with io.open(os.path.join(wf_directory, f"components-page-{position}-{page_id}.jsonl"), "w") as f:
            for p in page_components:
                f.write(json.dumps(p) + "\n")

def read_files(app_path: str) -> Tuple[MetadataDefinition, dict[str, ComponentDefinition]]:
    """
    Reads project files in the `.wf` folder.

    The components are read in page order.

    >>> metadata, components = wf_project.read_files('app/hello')
    """
    components: dict[str, ComponentDefinition] = {}

    meta_data_path = os.path.join(app_path, ".wf", "metadata.json")
    try:
        with io.open(meta_data_path, "r") as filep:
            metadata: MetadataDefinition = json.load(filep)
    except Exception as e:
        raise ValueError(f"Error reading metadata file {meta_data_path} : {e}")

    root_component_path = os.path.join(app_path, ".wf", "components-root.jsonl")
    try:
        with io.open(root_component_path, "r") as filep:
            root_component: ComponentDefinition = json.loads(filep.read())
            components.update({root_component["id"]: root_component})
    except Exception as e:
        raise ValueError(f"Error reading root component file {root_component_path} : {e}")

    files = os.listdir(os.path.join(app_path, ".wf"))
    page_files = [file for file in files if file.startswith("components-page-")]
    sorted_page_files = sorted(page_files, key=lambda x: int(x.split("-")[2]))
    for page_file in sorted_page_files:
        page_file_path = os.path.join(app_path, ".wf", page_file)
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

