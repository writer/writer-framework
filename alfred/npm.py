import alfred
import os

@alfred.command("npm.build", help="build ui code")
def npm_build():
    os.chdir("ui")
    alfred.run("npm run build")

@alfred.command("npm.build_custom_components", help="build custom components")
def ui_build_custom():
    os.chdir("ui")
    alfred.run("npm run custom.build")