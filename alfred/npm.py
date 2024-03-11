import alfred
import os

@alfred.command("npm.lint", help="lint check ui code")
def npm_lint():
    alfred.run("npm run lint:ci")

@alfred.command("npm.e2e", help="run e2e tests")
@alfred.option('--browser', '-b', help="run e2e tests on specified browser", default='chromium')
def npm_test(browser):
    alfred.run("npm run e2e:"+browser+":ci")

@alfred.command("npm.build", help="build ui code")
def npm_build():
    alfred.run("npm run build:ci")

@alfred.command("npm.build_custom_components", help="build custom components")
def ui_build_custom():
    alfred.run("npm run custom.build:ci")
