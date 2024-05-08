import tarfile
import requests
import os
from gitignore_parser import parse_gitignore

DEPLOY_URL = os.getenv("DEPLOY_URL", "https://api.writer.com/api/framework/deployment/apps")

def deploy(path, token):
    package = pack_project(path)
    upload_package(package, token)

def pack_project(path):
    print(f"Creating deployment package from path: {path}")

    files = []
    match = parse_gitignore(os.path.join(path, ".gitignore"))
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if ".git" in root.split(os.path.sep):
                continue
            if not match(os.path.join(root, filename)):
                files.append(os.path.relpath(os.path.join(root, filename), path))

    with tarfile.open("/tmp/streamsync_app.tar", "w") as tar:
        for file in files:
            print("Packing file:", file)
            tar.add(os.path.join(path, file), file)

    print("Streamsync app tar file created: /tmp/streamsync_app.tar")

    return "/tmp/streamsync_app.tar"


def upload_package(package, token):
    print("Uploading package to deployment server")
    files = {'file': open(package, 'rb')}
    with requests.post(
        url = DEPLOY_URL, 
        headers = {
            "Authorization": f"Bearer {token}",
        },
        files=files,
        stream=True
    ) as resp:
        for line in resp.iter_lines():
            if line:
                print(line.decode("utf-8"))
