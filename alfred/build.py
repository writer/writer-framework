import os.path
import shutil

import alfred


@alfred.command("build", help="build apps package for pypi")
@alfred.option("--ignore-ci", is_flag=True, help="ignore continuous integration pipeline")
def build(ignore_ci: bool = False):
    if not ignore_ci:
        alfred.invoke_command("ci")
    else:
        alfred.invoke_command("npm.build")

    alfred.invoke_command("build.app_provisionning")
    alfred.invoke_command("build.poetry")

@alfred.command("build.app_provisionning", help="update app templates using ./apps", hidden=True)
def build_app_provisionning():
    if os.path.isdir('src/writer/app_templates'):
        shutil.rmtree('src/writer/app_templates')

    shutil.copytree( 'apps/default', 'src/writer/app_templates/default')
    shutil.copytree( 'apps/hello', 'src/writer/app_templates/hello')

@alfred.command("build.poetry", help="build python packages with poetry", hidden=True)
def build_poetry():
    removed_directories = ['dist', 'build']
    for directory in removed_directories:
        if os.path.isdir(directory):
            shutil.rmtree(directory)

    alfred.run("poetry build")
