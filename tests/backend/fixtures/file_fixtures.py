"""
These fixtures simplify the writing of tests that read the results of files.
They reduce the boilerplate to write in tests.

>>> content: dict = file_fixtures.read('file.json')
"""
import io
import json
import os
from enum import Enum
from typing import Union


class FileFormat(Enum):
    auto = 'auto'
    json = 'json'
    jsonl = 'jsonl'
    txt = 'txt'

def read(path, format: FileFormat = FileFormat.auto) -> Union[str, dict, list]:
    """
    Read the contents of a file en fonction de son extension

    >>> read('test.json')
    {'key': 'value'}

    >>> read('test.jsonl')
    [{'key': 'value'}, {'key': 'value2'}]

    >>> read('test.any')

    For to use a specific format

    >>> read('test.any', format=FileFormat.json)
    """
    extension = os.path.splitext(path)[1]

    # If the format is auto, try to guess it from the extension
    format_mapping = {
        '.json': FileFormat.json,
        '.jsonl': FileFormat.jsonl,
        '.txt': FileFormat.txt
    }

    if format == FileFormat.auto:
        format = format_mapping.get(extension, FileFormat.txt)

    with io.open(path, 'r', encoding='utf-8') as filep:
        content = filep.read()
        if format == FileFormat.json:
            return json.loads(content)
        elif format == FileFormat.jsonl:
            output = []
            for line in content.splitlines():
                output.append(json.loads(line))
            return output
        else:
            return content
