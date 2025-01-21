import contextlib
from typing import Literal

import pytest
from writer.app_runner import AppRunner

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--full-run"):
        deselected = []
        selected = []
        for item in items:
            if "explicit" in item.keywords:
                deselected.append(item)
            else:
                selected.append(item)
        items[:] = selected
        config.hook.pytest_deselected(items=deselected)


def pytest_addoption(parser):
    parser.addoption(
        "--full-run", action="store_true", default=False, help="Include explicit-marked tests in the run (those are exluded from regular runs)"
    )

@pytest.fixture
def setup_app_runner():
    @contextlib.contextmanager
    def _manage_launch_args(app_dir: str, app_command: Literal["run", "edit"], load: bool = False):
        """
        Fixture to instantiate a writer application for testing.

        >>> with setup_app_runner("app_dir", "run", load=True) as ar:
        >>>     pass

        When the load flag is True, the application is loaded.

        >>> with setup_app_runner("app_dir", "run", load=True) as ar:
        >>>     pass

        :param app_dir: the folder that contains the application
        :param app_command: the execution mode of the application, either edit or run
        :param load: load the application if True
        """
        ar = AppRunner(app_dir, app_command)
        try:
            if load is True:
                ar.load()

            yield ar
        finally:
            ar.shut_down()
    return _manage_launch_args

@pytest.fixture(autouse=True)
def build_app_provisionning():
    import os
    import shutil

    root_dir = os.path.dirname(os.path.dirname(__file__))

    if os.path.isdir(os.path.join(root_dir, 'src/writer/app_templates')):
        shutil.rmtree(os.path.join(root_dir, 'src/writer/app_templates'))

    shutil.copytree( os.path.join(root_dir, 'apps'), os.path.join(root_dir, 'src/writer/app_templates'))