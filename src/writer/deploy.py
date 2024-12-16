import json
import logging
import os
import re
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timedelta
from typing import List, Union

import click
import dateutil.parser
import pytz
import requests
from gitignore_parser import parse_gitignore

DEPLOY_TIMEOUT = int(os.getenv("WRITER_DEPLOY_TIMEOUT", 20))

@click.group()
def cloud():
    """A group of commands to deploy the app on writer cloud"""
    pass

@cloud.command()
@click.option('--api-key',
    default=lambda: os.environ.get("WRITER_API_KEY", None),
    allow_from_autoenv=True,
    show_envvar=True,
    envvar='WRITER_API_KEY',
    prompt="Enter your API key",
    hide_input=True, help="Writer API key"
)
@click.option('--env', '-e', multiple=True, default=[], help="Set environment variables for the app (e.g., --env KEY=VALUE)")
@click.option('--force', '-f', default=False, is_flag=True, help="Ignores warnings and overwrites the app")
@click.option('--verbose', '-v', default=False, is_flag=True, help="Enable verbose mode")
@click.argument('path')
def deploy(path, api_key, env, verbose, force):
    """Deploy the app from PATH folder."""

    deploy_url = os.getenv("WRITER_DEPLOY_URL", "https://api.writer.com/v1/deployment/apps")
    sleep_interval = int(os.getenv("WRITER_DEPLOY_SLEEP_INTERVAL", '5'))

    if not force:
        check_app(deploy_url, api_key)

    abs_path = os.path.abspath(path)
    if not os.path.isdir(abs_path):
        raise click.ClickException("A path to a folder containing a Writer Framework app is required. For example: writer cloud deploy my_app")

    env = _validate_env_vars(env)
    tar = pack_project(abs_path)
    try:
        upload_package(deploy_url, tar, api_key, env, verbose=verbose, sleep_interval=sleep_interval)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            unauthorized_error()
        else:
            on_error_print_and_raise(e.response, verbose=verbose)
    except Exception as e:
        print(e)
        print("Error deploying app")
        sys.exit(1)
    finally:
        tar.close()

def _validate_env_vars(env: Union[List[str], None]) -> Union[List[str], None]:
    if env is None:
        return None
    for var in env:
        regex = r"^[a-zA-Z_]+[a-zA-Z0-9_]*=.*$"
        if not re.match(regex, var):
            logging.error(f"Invalid environment variable: {var}, please use the format ENV_VAR=value")
            sys.exit(1)
    return env

@cloud.command()
@click.option('--api-key',
    default=lambda: os.environ.get("WRITER_API_KEY", None),
    allow_from_autoenv=True,
    show_envvar=True,
    envvar='WRITER_API_KEY',
    prompt="Enter your API key",
    hide_input=True, help="Writer API key"
)
@click.option('--verbose', '-v', default=False, is_flag=True, help="Enable verbose mode")
def undeploy(api_key, verbose):
    """Stop the app, app would not be available anymore."""
    try:
        print("Undeploying app")
        deploy_url = os.getenv("WRITER_DEPLOY_URL", "https://api.writer.com/v1/deployment/apps")
        with requests.delete(deploy_url, headers={"Authorization": f"Bearer {api_key}"}) as resp:
            on_error_print_and_raise(resp, verbose=verbose)
            print("App undeployed")
            sys.exit(0)
    except Exception as e:
        print("Error undeploying app")
        print(e)
        sys.exit(1)

@cloud.command()
@click.option('--api-key',
    default=lambda: os.environ.get("WRITER_API_KEY", None),
    allow_from_autoenv=True,
    show_envvar=True,
    envvar='WRITER_API_KEY',
    prompt="Enter your API key",
    hide_input=True, help="Writer API key"
)
@click.option('--verbose', '-v', default=False, is_flag=True, help="Enable verbose mode")
def logs(api_key, verbose):
    """Fetch logs from the deployed app."""

    deploy_url = os.getenv("WRITER_DEPLOY_URL", "https://api.writer.com/v1/deployment/apps")
    sleep_interval = int(os.getenv("WRITER_DEPLOY_SLEEP_INTERVAL", '5'))

    try: 
        build_time = datetime.now(pytz.timezone('UTC')) - timedelta(days=4)
        start_time = build_time
        while True:
            prev_start = start_time
            end_time = datetime.now(pytz.timezone('UTC'))
            data = get_logs(deploy_url, api_key, {
                "buildTime": build_time,
                "startTime": start_time,
                "endTime": end_time,
            }, verbose=verbose)
            # order logs by date and print
            logs = data['logs']
            for log in logs:
                start_time = start_time if start_time > log[0] else log[0]
            if start_time == prev_start:
                start_time = datetime.now(pytz.timezone('UTC'))
                time.sleep(sleep_interval)
                continue
            for log in logs:
                print(log[0], log[1])
            print(start_time)
            time.sleep(sleep_interval)
    except Exception as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)

def pack_project(path):
    print(f"Creating deployment package from path: {path}")

    files = []
    def match(file_path) -> bool: return False
    if os.path.exists(os.path.join(path, ".gitignore")):
        match = parse_gitignore(os.path.join(path, ".gitignore"))
    for root, dirs, filenames in os.walk(path, followlinks=False):
        for filename in filenames:
            is_symlink = os.path.islink(os.path.relpath(os.path.join(root, filename), path))
            if is_symlink:
                print(f"[WARNING] Ignoring symlink: {os.path.relpath(os.path.join(root, filename), path)}")
                continue
            if "__pycache__" in root.split(os.path.sep):
                continue
            if ".git" in root.split(os.path.sep):
                continue
            if root == path and filename == "Dockerfile":
                print("[WARNING] Dockerfile found in project root. This will be ignored in the deployment package.")
                continue
            if root == path and filename == "service_entrypoint.py":
                print("[WARNING] service_entrypoint.py is a reserved file name. This will be ignored in the deployment package.")
                continue
            if not match(os.path.join(root, filename)):
                files.append(os.path.relpath(os.path.join(root, filename), path))

    f = tempfile.TemporaryFile(suffix='.tar')

    with tarfile.open(fileobj=f, mode="w") as tar:
        for file in files:
            print("Packing file:", file)
            tar.add(os.path.join(path, file), file)
    f.flush()

    return f

def check_app(deploy_url, token):
    url = _get_app_url(deploy_url, token)
    if url:
        print("[WARNING] This token was already used to deploy a different app")
        print(f"[WARNING] URL: {url}")
        print("[WARNING] If looking to deploy to a different URL, use a different API key. ")
        if input("[WARNING] Are you sure you want to overwrite? (y/N)").lower() != "y":
            sys.exit(1)

def _get_app_url(deploy_url: str, token: str) -> Union[str, None]:
    with requests.get(deploy_url, params={"lineLimit": 1}, headers={"Authorization": f"Bearer {token}"}) as resp:
        try:
            resp.raise_for_status()
        except Exception as e:
            print(e)
            print(resp.json())
            return None
        data = resp.json()
    return data['status']['url']

def get_logs(deploy_url, token, params, verbose=False):
    with requests.get(deploy_url, params = params, headers={"Authorization": f"Bearer {token}"}) as resp:
        on_error_print_and_raise(resp, verbose=verbose)
        data = resp.json()

        logs = []
        for log in data.get("logs", []):
            meta, msg = log["log"].split(" F ", 1)
            date, _ = meta.split(" ", 1)
            parsed_date = dateutil.parser.parse(date)
            logs.append((parsed_date, msg))
        logs.sort(key=lambda x: x[0])
        return {"status": data["status"], "logs": logs}

def check_service_status(deploy_url, token, build_id, build_time, start_time, end_time, last_status):
    data = get_logs(deploy_url, token, {
        "buildId": build_id,
        "buildTime": build_time,
        "startTime": start_time,
        "endTime": end_time
    })
    if data["status"]["status"] == "DEPLOYING" and data["status"]["status"] != last_status:
        print("Build completed. Deploying app...")
    status = data["status"]["status"]
    url = data["status"]["url"]
    for log in data.get("logs", []):
        print(log[0], log[1])
    return status, url

def dictFromEnv(env: List[str]) -> dict:
    env_dict = {}
    if env is None:
        return env_dict
    for e in env:
        key, value = e.split("=", 1)
        env_dict[key] = value
        print('Environment variable:', key)

    return env_dict


def upload_package(deploy_url, tar, token, env, verbose=False, sleep_interval=5):
    print("Uploading package to deployment server")
    tar.seek(0)
    files = {'file': tar}
    start_time = datetime.now(pytz.timezone('UTC'))
    build_time = start_time

    with requests.post(
        url = deploy_url, 
        headers = {
            "Authorization": f"Bearer {token}",
        },
        files=files,
        data={"envs": json.dumps(dictFromEnv(env))}
    ) as resp:
        on_error_print_and_raise(resp, verbose=verbose)
        data = resp.json()
        build_id = data["buildId"]

    print("Package uploaded. Building...")
    status = "WAITING"
    url = ""
    while status not in ["COMPLETED", "FAILED"] and datetime.now(pytz.timezone('UTC')) < build_time + timedelta(minutes=DEPLOY_TIMEOUT):
        end_time = datetime.now(pytz.timezone('UTC'))
        status, url = check_service_status(deploy_url, token, build_id, build_time, start_time, end_time, status)
        time.sleep(sleep_interval)
        start_time = end_time

    if status == "COMPLETED":
        print("Deployment successful")
        print(f"URL: {url}")
        sys.exit(0)
    elif status == "FAILED":
        print("Deployment failed")
        print(f"URL: {url}")
        sys.exit(1)
    else:
        time.sleep(sleep_interval)
        check_service_status(deploy_url, token, build_id, build_time, start_time, datetime.now(pytz.timezone('UTC')), status)
        print("Deployment status timeout")
        print(f"URL: {url}")
        sys.exit(2)

def on_error_print_and_raise(resp, verbose=False):
    try:
        resp.raise_for_status()
    except Exception as e:
        if verbose:
            print(resp.json())
        raise e

def unauthorized_error():
    print("Unauthorized. Please check your API key.")
    sys.exit(1)

