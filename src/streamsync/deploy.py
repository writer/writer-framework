import tarfile
import requests
import os
from gitignore_parser import parse_gitignore
import tempfile


WRITER_DEPLOY_URL = os.getenv("WRITER_DEPLOY_URL", "https://api.writer.com/api/framework/deployment/apps")

print("Deploying to:", WRITER_DEPLOY_URL)

def deploy(path, token):
    tar = pack_project(path)
    upload_package(tar, token)

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

    f = tempfile.TemporaryFile(suffix='.tar');

    with tarfile.open(fileobj=f, mode="w") as tar:
        for file in files:
            print("Packing file:", file)
            tar.add(os.path.join(path, file), file)
    f.flush()

    return f


def upload_package(tar, token):
    print("Uploading package to deployment server")
    tar.seek(0)
    files = {'file': tar}
    with requests.post(
        url = WRITER_DEPLOY_URL, 
        headers = {
            "Authorization": f"Bearer {token}",
        },
        files=files,
        stream=True
    ) as resp:
        for line in resp.iter_lines():
            if line:
                print(line.decode("utf-8"))
