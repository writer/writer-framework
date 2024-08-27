import io
import os.path

fixture_path = os.path.realpath(os.path.dirname(__file__))

def load_fixture_content(path) -> str:
    """
    Load the contents of a file from the fixture folder

    >>> c = load_fixture_content('obsoletes/ui_obsolete_visible.json')
    """
    with io.open(os.path.join(fixture_path, path), 'r', encoding='utf-8') as f:
        return f.read()
