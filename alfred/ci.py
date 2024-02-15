import os

import alfred


@alfred.command("ci", help="continuous integration pipeline")
def ci():
    alfred.invoke_command("ci.mypy")
    alfred.invoke_command("ci.pytest")
    alfred.invoke_command("npm.build")


@alfred.command("ci.mypy", help="typing checking with mypy on ./src/streamsync")
def ci_mypy():
    alfred.run("mypy ./src/streamsync --exclude app_templates/*")


@alfred.command("ci.pytest", help="run pytest on ./tests")
def ci_test():
    os.chdir("tests")
    alfred.run("pytest")