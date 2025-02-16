import contextlib
import os
import shutil
import tempfile
from typing import List

import alfred


@alfred.command("ci", help="continuous integration pipeline")
@alfred.option('--front', '-f', help="run for frontend only", is_flag=True, default=False)
@alfred.option('--docs', '-d', help="run for docs only", is_flag=True, default=False)
@alfred.option('--back', '-b', help="run for backend only", is_flag=True, default=False)
@alfred.option('--back-external', help="run for external test only", is_flag=True, default=False)
@alfred.option('--e2e', '-e', help="run for end-to-end only", default=None)
def ci(front, back, back_external, e2e, docs):
    no_flags = (not front and not back and not e2e and not docs)

    if front or no_flags:
        alfred.invoke_command("npm.lint")
        alfred.invoke_command("npm.build")
    if back or no_flags:
        alfred.invoke_command("ci.mypy")
        alfred.invoke_command("ci.ruff")
        alfred.invoke_command("ci.pytest.backend")
    if back_external or no_flags:
        alfred.invoke_command("ci.pytest.backend_external")
    if docs or no_flags:
        alfred.invoke_command("npm.docs.test")
    if e2e:
        alfred.invoke_command("npm.e2e", browser=e2e)

@alfred.command("ci.mypy", help="typing checking with mypy on ./src/writer")
def ci_mypy():
    alfred.run("mypy ./src/writer --exclude app_templates/*")

@alfred.command("ci.ruff", help="linting with ruff")
@alfred.option('--fix', '-f', help="fix linting errors", is_flag=True, default=False)
def ci_ruff(fix):
    if fix:
        alfred.run("ruff check --fix")
    else:
        alfred.run("ruff check")

@alfred.command("ci.pytest.backend", help="run pytest on ./tests")
def ci_pytest_backend():
    os.chdir("tests/backend")
    alfred.run("pytest")

@alfred.command("ci.pytest.backend_external", help="run automatic test on external integrations")
def ci_test_backend_external():
    os.chdir("tests/backend_external")
    alfred.run("pytest")


