import os

import alfred


@alfred.command("ci", help="continuous integration pipeline")
@alfred.option('--front', '-f', help="run for frontend only", is_flag=True, default=False)
@alfred.option('--back', '-b', help="run for backend only", is_flag=True, default=False)
@alfred.option('--e2e', '-e', help="run e2e tests", is_flag=True, default=False)
def ci(front, back, e2e):
    if back or (not front and not back and not e2e):
        alfred.invoke_command("ci.mypy")
        alfred.invoke_command("ci.pytest")
    if front or (not front and not back and not e2e):
        alfred.invoke_command("npm.lint")
        alfred.invoke_command("npm.build")
    if e2e or (not front and not back and not e2e):
        alfred.invoke_command("npm.e2e")

@alfred.command("ci.mypy", help="typing checking with mypy on ./src/streamsync")
def ci_mypy():
    alfred.run("mypy ./src/streamsync --exclude app_templates/*")


@alfred.command("ci.pytest", help="run pytest on ./tests")
def ci_test():
    os.chdir("tests")
    alfred.run("pytest")
