import tarfile
import requests
import os
from gitignore_parser import parse_gitignore


def deploy(path, token):
    package = pack_project(path)
    upload_package(package, token)

def pack_project(path):
    print("Creating deployment package from path: .", )

    files = []
    match = parse_gitignore(os.path.join(path, ".gitignore"))
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if not match(os.path.relpath(os.path.join(root, filename), path)):
                files.append(os.path.relpath(os.path.join(root, filename), path))

    with tarfile.open("/tmp/streamsync_app.tar", "w") as tar:
        for file in files:
            print("Packing file:", file)
            tar.add(os.path.join(path, file), file)

    print("Streamsync app tar file created: /tmp/streamsync_app.tar")

    return "/tmp/streamsync_app.tar"


def upload_package(package, token):
    print("Uploading package to deployment server")
    url = "http://localhost:8001/api/v1/namespaces/default/services/framework-deployment:80/proxy/api/framework/deployment/apps"
    files = {'file': open(package, 'rb')}
    with requests.post(
        url, 
        headers = {
            "Authorization": f"Bearer {token}",
            "applicationId": "1",
            "organizationId": "1"
        },
        files=files,
        stream=True
    ) as resp:
        for line in resp.iter_lines():
            if line:
                print(line.decode("utf-8"))
