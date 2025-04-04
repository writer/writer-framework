import contextlib
import os
import shutil
import tempfile
from typing import List

import alfred


@alfred.command("ci", help="continuous integration pipeline")
@alfred.option("--front", "-f", help="run for frontend only", is_flag=True, default=False)
@alfred.option("--back", "-b", help="run for backend only", is_flag=True, default=False)
@alfred.option("--e2e", "-e", help="run for end-to-end only", default=None)
def ci(front, back, e2e):
    no_flags = not front and not back and not e2e

    if front or no_flags:
        alfred.invoke_command("npm.lint")
        alfred.invoke_command("npm.build")
    if back or no_flags:
        alfred.invoke_command("ci.mypy")
        alfred.invoke_command("ci.ruff")
        alfred.invoke_command("ci.pytest")
    if e2e:
        alfred.invoke_command("npm.e2e", browser=e2e)


@alfred.command("ci.mypy", help="typing checking with mypy on ./src/writer")
def ci_mypy():
    alfred.run("mypy ./src/writer --exclude app_templates/*")


@alfred.command("ci.ruff", help="linting with ruff")
@alfred.option("--fix", "-f", help="fix linting errors", is_flag=True, default=False)
def ci_ruff(fix):
    if fix:
        alfred.run("ruff check --fix")
    else:
        alfred.run("ruff check")


@alfred.command("ci.pytest", help="run pytest on ./tests")
def ci_test():
    os.chdir("tests")
    alfred.run("pytest")


@alfred.command("ci.pytest.blocks", help="run pytest on ./tests")
def ci_test_blocks():
    os.chdir("tests")
    alfred.run("pytest backend/blocks")
