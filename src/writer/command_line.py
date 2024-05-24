import argparse
import getpass
import logging
import os
import shutil
import sys
from typing import Optional

import writer.deploy
import writer.serve


def main():
    parser = argparse.ArgumentParser(
        description="Run, edit or create a Writer Framework app.")
    parser.add_argument("command", choices=[
                        "run", "edit", "create", "hello", "deploy", "undeploy"])
    parser.add_argument(
        "path", nargs="?", help="Path to the app's folder")
    parser.add_argument(
        "--port", help="The port on which to run the server.")
    parser.add_argument(
        "--api-key", help="The API key to use for deployment.")
    parser.add_argument(
        "--host", help="The host on which to run the server. Use 0.0.0.0 to share in your local network.")
    parser.add_argument(
        "--enable-remote-edit", help="Set this flag to allow non-local requests in edit mode.", action='store_true')
    parser.add_argument(
        "--enable-server-setup", help="Set this flag to enable server setup hook in edit mode.", action='store_true')
    parser.add_argument(
        "--template", help="The template to use when creating a new app.")

    args = parser.parse_args()
    command = args.command
    default_port = 3006 if command in ("edit", "hello") else 3005
    enable_remote_edit = args.enable_remote_edit
    enable_server_setup_hook = args.enable_server_setup
    template_name = args.template

    port = int(args.port) if args.port else default_port
    absolute_app_path = _get_absolute_app_path(
        args.path) if args.path else None
    host = args.host if args.host else None
    api_key = args.api_key if args.api_key else None

    _perform_checks(command, absolute_app_path, host, enable_remote_edit, api_key)
    api_key = _get_api_key(command, api_key)
    _route(command, absolute_app_path, port, host, enable_remote_edit, enable_server_setup_hook, template_name, api_key)

def _get_api_key(command, api_key: Optional[str]) -> Optional[str]:
    if command in ("deploy", "undeploy") and api_key is None:
        env_key = os.getenv("WRITER_API_KEY", None)
        if env_key is not None and env_key != "": 
            return env_key
        else:
            logging.info("An API key is required to deploy a Writer Framework app.")
            api_key = getpass.getpass(prompt='Enter your API key: ', stream=None)
            if api_key is None or api_key == "":
                logging.error("No API key provided. Exiting.")
                sys.exit(1)
            return api_key
    else:
        return api_key


def _perform_checks(command: str, absolute_app_path: str, host: Optional[str], enable_remote_edit: Optional[bool], api_key: Optional[str] = None):
    is_path_folder = absolute_app_path is not None and os.path.isdir(absolute_app_path)

    if command in ("run", "edit", "deploy") and is_path_folder is False:
        logging.error("A path to a folder containing a Writer Framework app is required. For example: writer edit my_app")
        sys.exit(1)

    if command in ("create") and absolute_app_path is None:
        logging.error("A target folder is required to create a Writer Framework app. For example: writer create my_app")
        sys.exit(1)

    if command in ("edit", "hello") and host is not None:
        logging.warning("Writer Framework has been enabled in edit mode with a host argument\nThis is enabled for local development purposes (such as a local VM).\nDon't expose Builder to the Internet. We recommend using a SSH tunnel instead.")

    if command in ("edit", "hello") and enable_remote_edit is True:
        logging.warning("The remote edit flag is active. Builder will accept non-local requests. Please make sure the host is protected to avoid drive-by attacks.")


def _route(
    command: str,
    absolute_app_path: str,
    port: int,
    host: Optional[str],
    enable_remote_edit: Optional[bool],
    enable_server_setup: Optional[bool],
    template_name: Optional[str],
    api_key: Optional[str] = None
):
    if host is None:
        host = "127.0.0.1"
    if command in ("deploy"):
        writer.deploy.deploy(absolute_app_path, api_key)
    if command in ("undeploy"):
        writer.deploy.undeploy(api_key)
    if command in ("edit"):
        writer.serve.serve(
            absolute_app_path, mode="edit", port=port, host=host,
            enable_remote_edit=enable_remote_edit, enable_server_setup=enable_server_setup)
    if command in ("run"):
        writer.serve.serve(
            absolute_app_path, mode="run", port=port, host=host, enable_server_setup=True)
    elif command in ("hello"):
        create_app("hello", template_name="hello", overwrite=True)
        writer.serve.serve("hello", mode="edit",
                               port=port, host=host, enable_remote_edit=enable_remote_edit,
                               enable_server_setup=False)
    elif command in ("create"):
        create_app(absolute_app_path, template_name=template_name)

def create_app(app_path: str, template_name: Optional[str], overwrite=False):
    if template_name is None:
        template_name = "default"

    is_folder_created = os.path.exists(app_path)
    is_folder_empty = True if not is_folder_created else len(os.listdir(app_path)) == 0

    if not overwrite and not is_folder_empty:
        logging.error("The target folder must be empty or not already exist.")
        sys.exit(1)

    server_path = os.path.dirname(__file__)
    template_path = os.path.join(server_path, "app_templates", template_name)

    if not os.path.exists(template_path):
        logging.error(f"Template { template_name } couldn't be found.")
        sys.exit(1)

    shutil.copytree(template_path, app_path, dirs_exist_ok=True)


def _get_absolute_app_path(app_path: str):
    is_path_absolute = os.path.isabs(app_path)
    if is_path_absolute:
        return app_path
    else:
        return os.path.join(os.getcwd(), app_path)



if __name__ == "__main__":
    main()
