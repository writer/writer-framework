import alfred


@alfred.command("install.dev", help="install developper dependencies and generate code")
def install_dev():
    alfred.run("poetry install --with build")
    alfred.run("npm ci")
    alfred.invoke_command("npm.codegen")

@alfred.command("install.ci", help="install ci dependencies and generate code", hidden=True)
def install_ci():
    alfred.run("npm ci")
    alfred.invoke_command("npm.codegen")
