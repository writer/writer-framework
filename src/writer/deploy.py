import os
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timedelta

import pytz
import requests
from gitignore_parser import parse_gitignore

WRITER_DEPLOY_URL = os.getenv("WRITER_DEPLOY_URL", "https://api.writer.com/v1/deployment/apps")

def deploy(path, token):
    tar = pack_project(path)
    upload_package(tar, token)

def undeploy(token):
    try:
        print("Undeploying app")
        with requests.delete(WRITER_DEPLOY_URL, headers={"Authorization": f"Bearer {token}"}) as resp:
            resp.raise_for_status()
            print("App undeployed")
            sys.exit(0)
    except Exception as e:
        print("Error undeploying app")
        print(e)
        sys.exit(1)

def pack_project(path):
    print(f"Creating deployment package from path: {path}")

    files = []
    def match(file_path) -> bool: return False
    if os.path.exists(os.path.join(path, ".gitignore")):
        match = parse_gitignore(os.path.join(path, ".gitignore"))
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if ".git" in root.split(os.path.sep):
                continue
            if filename == "Dockerfile":
                print("[WARNING] Dockerfile found in project root. This will be ignored in the deployment package.")
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


def upload_package(tar, token):
    try: 
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
            stream=True
        ) as resp:
            resp.raise_for_status()
            data = resp.json()
            build_id = data["buildId"]
        print("Package uploaded. Building...")
        status = "WAITING"
        url = ""
        while status not in ["COMPLETED", "FAILED"] and datetime.now(pytz.timezone('UTC')) < start_time + timedelta(minutes=5):
            end_time = datetime.now(pytz.timezone('UTC'))
            with requests.get(WRITER_DEPLOY_URL, params = {
                "buildId": build_id,
                "buildTime": build_time.isoformat(),
                "startTime": start_time.isoformat(),
                "endTime": end_time.isoformat()
            }, headers={"Authorization": f"Bearer {token}"}) as resp:
                resp.raise_for_status()
                data = resp.json()
                #print(data["status"])
                if data["status"]["status"] == "DEPLOYING" and data["status"]["status"] != status:
                    print("Build completed. Deploying app...")
                status = data["status"]["status"]
                url = data["status"]["url"]
                for log in data.get("logs", []):
                    print(log["log"])
            time.sleep(5)
            start_time = end_time

        if status == "COMPLETED":
            print("Deployment successful")
            print(f"URL: {url}")
            sys.exit(0)
        else:
            print("Deployment failed")
            sys.exit(1)

    except Exception as e:
        print("Error uploading package")
        print(e)
        sys.exit(1)
    finally:
        tar.close()
