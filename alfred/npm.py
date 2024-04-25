import os

import alfred


@alfred.command("npm.lint", help="lint check npm packages")
def npm_lint():
    alfred.run("npm run ui:lint:ci")

@alfred.command("npm.e2e", help="run e2e tests")
@alfred.option('--browser', '-b', help="run e2e tests on specified browser", default='chromium')
def npm_e2e(browser):
    with alfred.env(CI="true"):
        alfred.run("npm run e2e:"+browser)

@alfred.command("npm.build", help="build ui code")
def npm_build():
    alfred.run("npm run ui:build")

@alfred.command("npm.build_custom_components", help="build custom components")
def npm_build_custom_components():
    alfred.run("npm run ui:custom.build")

@alfred.command("npm.docs", help="build docs", hidden=True)
def npm_docs():
    alfred.run("npm run docs:build")

@alfred.command("npm.docs.test", help="test against documentation")
def npm_docs_test():
    alfred.run("npm run docs:test")

@alfred.command("npm.storybook", help="build storybook for continuous integration")
def npm_storybook():
    os.chdir("src/ui")
    alfred.run("npm run storybook.build")

@alfred.command("npm.codegen", help="generate code for low code ui")
def npm_codegen():
    alfred.run("npm run ui:codegen")
    alfred.run("npm run docs:codegen")
