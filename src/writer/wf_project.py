"""
This module manipulates the folder of a wf project stored into `wf`.

>>> wf_project.write_files_async('app/hello', metadata={"writer_version": "0.1" }, components=...)

>>> metadata, components = wf_project.read_files('app/hello')
"""
import dataclasses
import glob
import hashlib
import io
import json
import logging
import multiprocessing
import os
import queue
import time
import typing
from collections import OrderedDict
from multiprocessing import Queue
from typing import Any, Dict, List, Tuple

from writer import core_ui
from writer.ss_types import ComponentDefinition, MetadataDefinition, SourceFilesDirectory

ROOTS = ['root', 'blueprints_root']
COMPONENT_ROOTS = ['page', 'blueprints_blueprint']

shared_queue_write_files: typing.Optional[Queue] = None

@dataclasses.dataclass
class WfProjectContext:
    app_path: str
    write_files_async_queue: Queue = dataclasses.field(default_factory=Queue)
    write_files_async_process: typing.Optional[multiprocessing.Process] = None
    write_files_async_stop: Any = dataclasses.field(default_factory=multiprocessing.Event)  # Note: Event is a function, not a class in python, it can't be typed
    file_hashes: Dict[str, str] = dataclasses.field(default_factory=dict)


def write_files_async(context: WfProjectContext, metadata: MetadataDefinition, components: Dict[str, ComponentDefinition]) -> None:
    """
    This operation is asynchrone. It's managed in wf_project.process_write_files_async.

    see wf_project.write_files for description

    >>> wf_project.write_files_async('app/hello', metadata={"writer_version": "0.1" }, components=...)
    """
    
    while not context.write_files_async_queue.empty():
        try:
            context.write_files_async_queue.get_nowait()
        except queue.Empty:
            break

    context.write_files_async_queue.put((context.app_path, metadata, components))

def write_files(app_path: str, metadata: MetadataDefinition, components: Dict[str, ComponentDefinition], context: WfProjectContext) -> None:
    """
    Writes the meta data of the WF project to the `.wf` directory (metadata, components, ...).

    * the metadata.json file is written in json format
    * a file for the root component written in jsonline format
    * a file for the blueprints_root component written in jsonline format
    * one file per page is created in the form `components-page-{id}.json` in jsonline format
    * one file per blueprint is created in the form `components-blueprints_blueprint-{id}.json` in jsonline format

    >>> wf_project.write_files('app/hello', metadata={"writer_version": "0.1" }, components=..., context=wf_project.WfProjectContext(app_path="app/path"))
    """

    wf_directory = os.path.join(app_path, ".wf")
    if not os.path.exists(wf_directory):
        os.makedirs(wf_directory)

    with io.open(os.path.join(wf_directory, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)
        f.flush()
        os.fsync(f.fileno())

    logger = logging.getLogger("writer")
    time_start = time.time()
    logger.info("Saving project...")
    _write_root_files(wf_directory, components, context)
    _write_component_files(wf_directory, components, context)
    _remove_obsolete_component_files(wf_directory, components)
    logger.info("Saved. Time elapsed: %.4fs", time.time() - time_start)


def start_process_write_files_async(context: WfProjectContext, save_interval: float) -> None:
    """
    Creates a process that writes the .wf/ files

    This agent allows you to process the backup of .wf files in the background
    without blocking application requests.

    :param wf_project_save_interval: the interval in seconds to save the project files
    :return:
    """
    p = multiprocessing.Process(
        target=_start_process_write_files_async_process,
        args=(context, save_interval, context.write_files_async_stop)
    )
    context.write_files_async_process = p
    p.start()


def shutdown_process_write_files_async(context: WfProjectContext) -> None:
    """
    Shutdown the process that writes the .wf/ files
    """
    if context.write_files_async_process is not None and \
        context.write_files_async_process.is_alive():
        context.write_files_async_stop.set()
        context.write_files_async_process.join()
        context.write_files_async_process = None
        context.write_files_async_stop.clear()

def read_files(app_path: str) -> Tuple[MetadataDefinition, dict[str, ComponentDefinition]]:
    """
    Reads project files in the `.wf` folder.

    The components are read in page and blueprints_blueprint order.

    >>> metadata, components = wf_project.read_files('app/hello')
    """
    components: dict[str, ComponentDefinition] = {}
    roots = ['root', 'blueprints_root']
    component_part_file_type = ['page', 'blueprints_blueprint']

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


def create_default_blueprints_root(abs_path: str) -> None:
    with io.open(os.path.join(abs_path, '.wf', 'components-blueprints_root.jsonl'), 'w') as f:
        f.write('{"id": "blueprints_root", "type": "blueprints_root", "content": {}, "isCodeManaged": false, "position": 0, "handlers": {}, "visible": {"expression": true, "binding": "", "reversed": false}}')
        logger = logging.getLogger('writer')
        logger.warning('project format has changed and has been migrated with success. components-blueprints_root.jsonl has been added.')
        f.flush()
        os.fsync(f.fileno())


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


def _write_component_files(wf_directory: str, components: Dict[str, ComponentDefinition], context: WfProjectContext) -> None:
    """
    Writes the component files in the .wf folder. It preserve obsolete files.

    The components are written in the form `components-{type}-{position}-{id}.jsonl`
    """
    for component_id, filename in _expected_component_fileinfos(components):
        filtered_components = core_ui.filter_components_by(components, parent=component_id)

        file_path = os.path.join(wf_directory, filename)
        file_contents = "".join(
            [json.dumps(_sort_wf_component_keys(p)) + "\n" for p in _order_components(filtered_components)]
        )

        has_changed = _has_file_hash_changed(filename, file_contents, context)
        if not has_changed:
            continue

        with io.open(file_path, "w") as f:
            f.write(file_contents)
            f.flush()
            os.fsync(f.fileno())


def _write_root_files(wf_directory, components, context: WfProjectContext):
    for root in ROOTS:
        root_component = components.get(root, None)
        if root_component:
            file_contents = json.dumps(_sort_wf_component_keys(root_component))

            has_changed = _has_file_hash_changed(f"components-{root}.jsonl", file_contents, context)
            if not has_changed:
                continue

            with io.open(os.path.join(wf_directory, f"components-{root}.jsonl"), "w") as f:
                f.write(file_contents)
                f.flush()
                os.fsync(f.fileno())


def _has_file_hash_changed(file_name: str, new_contents: str, context: WfProjectContext) -> bool:
    """
    Returns whether a hash of a file changed given new file contents;

    Missing file counts as hash invalidation and return True.
    """
    new_hash = hashlib.md5(new_contents.encode('utf-8')).hexdigest()

    old_hash = context.file_hashes.get(file_name)
    context.file_hashes[file_name] = new_hash
    return old_hash != new_hash


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


def _start_process_write_files_async_process(context: WfProjectContext, save_interval, stop_event):
    while True:
        if stop_event.is_set():
            break

        try:
            obj = context.write_files_async_queue.get(block=False)
        except queue.Empty:
            obj = None

        if obj is not None:
            app_path, metadata, components = obj
            write_files(app_path, metadata, components, context)

        time.sleep(save_interval)


def is_project(path: str) -> bool:
    """
    Returns True if the path is a Writer Framework project.

    >>> wf_project.is_project('app/hello')
    """
    has_main_py = os.path.isfile(os.path.join(path, "main.py"))
    has_wf_directory = os.path.isdir(os.path.join(path, ".wf"))

    return has_main_py and has_wf_directory


def can_create_project(path: str) -> bool:
    """
    Returns True the path does not contain a Writer Framework project and
    it is possible to create one automatically.

    >>> wf_project.can_create_project('app/hello')
    """
    if not os.path.isdir(path):
        return True

    if len(os.listdir(path)) == 0:
        return True

    return False


def build_source_files(app_path: str) -> SourceFilesDirectory:
    """
    Build a file tree as `Dict` wherein the key represent the filename. The value is a `Dict` with a `type` as:

    - `directory`, so it's a directory containing `children`
    - `file`, so it's a file with `content` as string. We limit the file to the first X characters and set `"complete": False` if content is truncated

    Example:

    >>> {'type': 'directory', 'children': {'README.md': {'type': 'file', 'content': 'This app w', 'complete': False}}}
    """
    def load_persisted_script(file: str) -> str:
        path = os.path.join(app_path, file)
        with open(path, "r", encoding='utf-8') as f:
            return f.read()


    ignore_dirs = ['.venv', 'venv', '__pycache__', '.wf']
    ignore_files = ['.DS_Store']
    files = []
    for root, dirs, filenames in os.walk(app_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for filename in filenames:
            if filename not in ignore_files:
                files.append(os.path.realpath(os.path.join(root, filename)))

    file_tree: SourceFilesDirectory = { "type": "directory", "children": {} }

    for file in files:
        relative_path = os.path.relpath(file, app_path)
        parts = relative_path.split(os.sep)
        current_level: SourceFilesDirectory = file_tree

        for i, part in enumerate(parts):
            if os.path.isdir(os.path.join(app_path, *parts[: i + 1])):
                if part not in current_level["children"]:
                    current_level["children"][part] = { "type": "directory", "children": {} }

                next_level = current_level["children"][part]

                if next_level["type"] == "directory":
                    current_level = next_level
            else:
                try:
                    content = load_persisted_script(relative_path)
                    extension = os.path.splitext(relative_path)[1]
                    # limit only the first 100 characters to limit bandwidth usage, the rest will be lazy loaded
                    excerpt = content if extension == '.py' else content[0:100]
                    current_level["children"][part] = {
                        "type": "file",
                        "content": excerpt,
                        "complete": excerpt == content,
                    }
                except UnicodeDecodeError:
                    # TODO: get mimetype
                    current_level["children"][part] = { "type": "binary" }
                except  FileNotFoundError:
                    pass

    return file_tree
