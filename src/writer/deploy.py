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

WRITER_DEPLOY_URL = os.getenv("WRITER_DEPLOY_URL", "https://api.writer.com/v1/deployment/apps")

@click.group()
def cloud():
    """A group of commands to deploy the app"""
    pass

@click.command()
@click.option('--api-key', default=lambda: os.environ.get("WRITER_API_KEY", None), prompt=True, hide_input=True, help="Writer API key")
@click.option('--env', multiple=True, default=[], help="Environment to deploy the app to")
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def deploy(path, api_key, env):
    """Deploy the app from PATH folder."""
    env = _validate_env_vars(env)
    tar = pack_project(path)
    try:
        upload_package(tar, api_key, env)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            unauthorized_error()
        print(e)
        print("Error deploying app")
        sys.exit(1)
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
        print(var)
        regex = r"^[a-zA-Z_]+[a-zA-Z0-9_]*=.*$"
        if not re.match(regex, var):
            logging.error(f"Invalid environment variable: {var}, please use the format ENV_VAR=value")
            sys.exit(1)
    return env

@click.command()
@click.option('--api-key', default=lambda: os.environ.get("WRITER_API_KEY", None), prompt=True, hide_input=True, help="Writer API key")
def undeploy(api_key):
    """Stop the app, app would not be available anymore."""
    try:
        print("Undeploying app")
        with requests.delete(WRITER_DEPLOY_URL, headers={"Authorization": f"Bearer {api_key}"}) as resp:
            on_error_print_and_raise(resp)
            print("App undeployed")
            sys.exit(0)
    except Exception as e:
        print("Error undeploying app")
        print(e)
        sys.exit(1)

@click.command()
@click.option('--api-key',
    default=lambda: os.environ.get("WRITER_API_KEY", None),
    allow_from_autoenv=True,
    show_envvar=True,
    envvar='WRITER_API_KEY',
    prompt="Enter your API key",
    hide_input=True, help="Writer API key"
)
def logs(api_key):
    """Fetch logs from the deployed app."""
    try: 
        build_time = datetime.now(pytz.timezone('UTC')) - timedelta(days=4)
        start_time = build_time
        while True:
            prev_start = start_time
            end_time = datetime.now(pytz.timezone('UTC'))
            data = get_logs(api_key, {
                "buildTime": build_time,
                "startTime": start_time,
                "endTime": end_time,
            })
            # order logs by date and print
            logs = data['logs']
            for log in logs:
                start_time = start_time if start_time > log[0] else log[0]
            if start_time == prev_start:
                start_time = datetime.now(pytz.timezone('UTC'))
                time.sleep(5)
                continue
            for log in logs:
                print(log[0], log[1])
            print(start_time)
            time.sleep(1)
    except Exception as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)

cloud.add_command(deploy)
cloud.add_command(undeploy)
cloud.add_command(logs)

def pack_project(path):
    print(f"Creating deployment package from path: {path}")

    files = []
    def match(file_path) -> bool: return False
    if os.path.exists(os.path.join(path, ".gitignore")):
        match = parse_gitignore(os.path.join(path, ".gitignore"))
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
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

def get_logs(token, params):
    with requests.get(WRITER_DEPLOY_URL, params = params, headers={"Authorization": f"Bearer {token}"}) as resp:
        on_error_print_and_raise(resp)
        data = resp.json()

        logs = []
        for log in data.get("logs", []):
            meta, msg = log["log"].split(" F ", 1)
            date, _ = meta.split(" ", 1)
            parsed_date = dateutil.parser.parse(date)
            logs.append((parsed_date, msg))
        logs.sort(key=lambda x: x[0])
        return {"status": data["status"], "logs": logs}

def check_service_status(token, build_id, build_time, start_time, end_time, last_status):
    data = get_logs(token, {
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


def upload_package(tar, token, env):
    print("Uploading package to deployment server")
    tar.seek(0)
    files = {'file': tar}
    start_time = datetime.now(pytz.timezone('UTC'))
    build_time = start_time
    with requests.post(
        url = WRITER_DEPLOY_URL, 
        headers = {
            "Authorization": f"Bearer {token}",
        },
        files=files,
        data={"envs": json.dumps(dictFromEnv(env))}
    ) as resp:
        on_error_print_and_raise(resp)
        data = resp.json()
        build_id = data["buildId"]

    print("Package uploaded. Building...")
    status = "WAITING"
    url = ""
    while status not in ["COMPLETED", "FAILED"] and datetime.now(pytz.timezone('UTC')) < build_time + timedelta(minutes=5):
        end_time = datetime.now(pytz.timezone('UTC'))
        status, url = check_service_status(token, build_id, build_time, start_time, end_time, status)
        time.sleep(5)
        start_time = end_time

    if status == "COMPLETED":
        print("Deployment successful")
        print(f"URL: {url}")
        sys.exit(0)
    else:
        time.sleep(5)
        check_service_status(token, build_id, build_time, start_time, datetime.now(pytz.timezone('UTC')), status)
        print("Deployment failed")
        sys.exit(1)

def on_error_print_and_raise(resp):
    try:
        resp.raise_for_status()
    except Exception as e:
        if os.getenv('DEBUG') == 'true':
            print(resp.json())
        raise e

def unauthorized_error():
    print(f"\n{WRITER_DEPLOY_URL}")
    print("Unauthorized. Please check your API key.")
    sys.exit(1)
