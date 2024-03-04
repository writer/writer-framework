import alfred
import os

@alfred.command("npm.lint", help="lint check ui code")
def npm_lint():
    alfred.run("npm run lint:ci")

@alfred.command("npm.e2e", help="run e2e tests")
def npm_test():
    alfred.run("npm run e2e:ci")

@alfred.command("npm.build", help="build ui code")
def npm_build():
    alfred.run("npm run build")

@alfred.command("npm.build_custom_components", help="build custom components")
def ui_build_custom():
    alfred.run("npm run custom.build")
