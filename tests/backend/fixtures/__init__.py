import os.path
from typing import Union

from . import file_fixtures

fixture_path = os.path.realpath(os.path.dirname(__file__))


def load_fixture_content(path, format: file_fixtures.FileFormat = file_fixtures.FileFormat.auto) -> Union[str, dict, list]:
    """
    Load the contents of a file from the fixture folder
    >>> c = load_fixture_content('obsoletes/ui_obsolete_visible.json')
    """
    file_path = os.path.join(fixture_path, path)
    return file_fixtures.read(file_path, format)
