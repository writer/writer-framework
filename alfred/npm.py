import alfred
import os

@alfred.command("npm.lint", help="lint check ui code")
def npm_lint():
    os.chdir("ui")
    alfred.run("npm run lint:ci")

@alfred.command("npm.e2e", help="run e2e tests")
def npm_test():
    os.chdir("e2e_tests")
    alfred.run("npm run test:ci")

@alfred.command("npm.build", help="build ui code")
def npm_build():
    os.chdir("ui")
    alfred.run("npm run build")

@alfred.command("npm.build_custom_components", help="build custom components")
def ui_build_custom():
    os.chdir("ui")
    alfred.run("npm run custom.build")
