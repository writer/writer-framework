import sys
from typing import Optional
import streamsync.serve
import argparse
import os
import logging
import shutil


def main():
    parser = argparse.ArgumentParser(
        description="Run, edit or create a Streamsync app.")
    parser.add_argument("command", choices=[
                        "run", "edit", "create", "hello"])
    parser.add_argument(
        "path", nargs="?", help="Path to the app's folder")
    parser.add_argument(
        "--port", help="The port on which to run the server.")
    parser.add_argument(
        "--host", help="The host on which to run the server. Use 0.0.0.0 to share in your local network.")
    parser.add_argument(
        "--enable-remote-edit", help="Set this flag to allow non-local requests in edit mode.", action='store_true')

    args = parser.parse_args()
    command = args.command
    default_port = 3006 if command in ("edit", "hello") else 3005
    enable_remote_edit = args.enable_remote_edit

    port = int(args.port) if args.port else default_port
    absolute_app_path = _get_absolute_app_path(
        args.path) if args.path else None
    host = args.host if args.host else None

    _perform_checks(command, absolute_app_path, host, enable_remote_edit)
    _route(command, absolute_app_path, port, host, enable_remote_edit)

def _perform_checks(command: str, absolute_app_path: str, host: Optional[str], enable_remote_edit: Optional[bool]):
    is_path_folder = absolute_app_path is not None and os.path.isdir(absolute_app_path)

    if command in ("run", "edit") and is_path_folder is False:
        logging.error("A path to a folder containing a Streamsync app is required. For example: streamsync edit my_app")
        sys.exit(1)

    if command in ("create") and absolute_app_path is None:
        logging.error("A target folder is required to create a Streamsync app. For example: streamsync create my_app")
        sys.exit(1)

    if command in ("edit", "hello") and host is not None:
        logging.warning("Streamsync has been enabled in edit mode with a host argument\nThis is enabled for local development purposes (such as a local VM).\nDon't expose Streamsync Builder to the Internet. We recommend using a SSH tunnel instead.")

    if command in ("edit", "hello") and enable_remote_edit is True:
        logging.warning("The remote edit flag is active. Streamsync Builder will accept non-local requests. Please make sure the host is protected to avoid drive-by attacks.")

    if command in ("hello"):
        try:
            import pandas
            import pyarrow # type: ignore
            import plotly.express # type: ignore
        except ImportError:
            logging.error("Running streamsync hello requires pandas, pyarrow and plotly.express. Install them with:\npip install streamsync[ds]")
            sys.exit(1)


def _route(command: str, absolute_app_path: str, port: int, host: Optional[str], enable_remote_edit: Optional[bool]):
    if host is None:
        host = "127.0.0.1"
    if command in ("edit"):
        streamsync.serve.serve(
            absolute_app_path, mode="edit", port=port, host=host, enable_remote_edit=enable_remote_edit)
    if command in ("run"):
        streamsync.serve.serve(
            absolute_app_path, mode="run", port=port, host=host)
    elif command in ("hello"):
        create_app("hello", template_name="hello", overwrite=True)
        streamsync.serve.serve("hello", mode="edit",
                               port=port, host=host, enable_remote_edit=enable_remote_edit)
    elif command in ("create"):
        create_app(absolute_app_path)

def create_app(app_path: str, template_name: str = "default", overwrite=False):
    is_folder_created = os.path.exists(app_path)
    is_folder_empty = True if not is_folder_created else len(os.listdir(app_path)) == 0

    if not overwrite and not is_folder_empty:
        logging.error("The target folder must be empty or not already exist.")
        sys.exit(1)

    server_path = os.path.dirname(__file__)
    template_path = os.path.join(server_path, "app_templates", template_name)
    shutil.copytree(template_path, app_path, dirs_exist_ok=True)


def _get_absolute_app_path(app_path: str):
    is_path_absolute = os.path.isabs(app_path)
    if is_path_absolute:
        return app_path
    else:
        return os.path.join(os.getcwd(), app_path)



if __name__ == "__main__":
    main()
