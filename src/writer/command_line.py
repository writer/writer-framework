import os
import shutil
from typing import Optional

import click

import writer.serve
from writer import VERSION, wf_project
from writer.deploy import cloud, deploy

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}
@click.group(
    context_settings=CONTEXT_SETTINGS,
    help="Writer Framework CLI",
)
@click.version_option(None, '--version', '-v')
def main():
    pass

@main.command()
@click.option('--host', default="127.0.0.1", help="Host to run the app on")
@click.option('--port', default=None, help="Port to run the app on")
@click.option("--enable-jobs-api", help="Set this flag to enable the Jobs API, allowing you to execute jobs without user interaction.", is_flag=True)
@click.argument('path')
def run(path: str, host: str, port: Optional[int], enable_jobs_api: bool):
    """Run the app from PATH folder in run mode."""

    abs_path = os.path.abspath(path)
    if wf_project.is_project(path) is False and \
        wf_project.can_create_project(path) is True:
        raise click.ClickException(f"There's no Writer Framework project at this location, create a new one with `writer create {path}`")

    if wf_project.is_project(path) is False and \
        wf_project.can_create_project(path) is False:
        raise click.ClickException(f"There's no Writer Framework project at this location : {abs_path}")

    writer.serve.serve(
        abs_path, mode="run", port=port, host=host, enable_server_setup=True, enable_jobs_api=enable_jobs_api)

@main.command()
@click.option('--host', default="127.0.0.1", help="Host to run the app on")
@click.option('--port', default=None, help="Port to run the app on")
@click.option('--enable-remote-edit', help="Set this flag to allow non-local requests in edit mode.", is_flag=True)
@click.option('--enable-server-setup', help="Set this flag to enable server setup hook in edit mode.", is_flag=True)
@click.option("--no-interactive", help="Set this flag to run the app without asking anything to the user.", is_flag=True)
@click.option("--enable-jobs-api", help="Set this flag to enable the Jobs API, allowing you to execute jobs without user interaction.", is_flag=True)
@click.argument('path')
def edit(
    path: str,
    port: Optional[int],
    host: str,
    enable_remote_edit: bool,
    enable_server_setup: bool,
    no_interactive: bool,
    enable_jobs_api: bool,
):
    """Run the app from PATH folder in edit mode."""
    abs_path = os.path.abspath(path)
    if wf_project.is_project(path) is False and \
        wf_project.can_create_project(path) is True and \
        no_interactive is False:
        click.confirm("There’s no Writer Framework project at this location, would you like to create a new one ?", default=False, abort=True)
        create_app(path, template_name="default", overwrite=False)

    if wf_project.is_project(path) is False and \
        wf_project.can_create_project(path) is True:
        raise click.ClickException(f"There’s no Writer Framework project at this location, create a new one with `writer create {path}`")

    if wf_project.is_project(path) is False and \
        wf_project.can_create_project(path) is False:
        raise click.ClickException(f"There’s no Writer Framework project at this location : {abs_path}")

    writer.serve.serve(
        abs_path, mode="edit", port=port, host=host,
        enable_remote_edit=enable_remote_edit, enable_server_setup=enable_server_setup, enable_jobs_api=enable_jobs_api)

@main.command()
@click.argument('path')
@click.option('--template', help="The template to use when creating a new app.")
def create(path, template):
    """Create a new app in PATH folder."""

    abs_path = os.path.abspath(path)
    if os.path.isfile(abs_path):
        raise click.ClickException("A target folder is required to create a Writer Framework app. For example: writer create my_app")

    create_app(os.path.abspath(path), template_name=template)

@main.command()
@click.option('--host', default="127.0.0.1", help="Host to run the app on")
@click.option('--port', default=None, help="Port to run the app on")
@click.option('--enable-remote-edit', help="Set this flag to allow non-local requests in edit mode.", is_flag=True)
def hello(port: Optional[int], host: str, enable_remote_edit):
    """Create and run an onboarding 'Hello' app."""
    create_app("hello", template_name="hello", overwrite=True)
    writer.serve.serve("hello", mode="edit",
       port=port, host=host, enable_remote_edit=enable_remote_edit,
       enable_server_setup=False)


main.add_command(deploy, name="deploy")
main.add_command(cloud)

def create_app(app_path: str, template_name: Optional[str], overwrite=False):
    if template_name is None:
        template_name = "default"

    if wf_project.can_create_project(path=app_path) is False:
        raise click.ClickException("The target folder must be empty or not already exist.")

    server_path = os.path.dirname(__file__)
    template_path = os.path.join(server_path, "app_templates", template_name)

    if not os.path.exists(template_path):
        raise click.ClickException(f"Template { template_name } couldn't be found.")

    shutil.copytree(template_path, app_path, dirs_exist_ok=True)
    # create/update requirements.txt and add writer to it
    requirements_path = os.path.join(app_path, "requirements.txt")
    with open(requirements_path, "a") as f:
        f.write(f"writer=={VERSION}\n")


if __name__ == "__main__":
    main()
