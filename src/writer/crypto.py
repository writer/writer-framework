
import hashlib
import os

from fastapi import HTTPException, Request

HASH_SALT = "a9zHYfIeL0"

def get_hash(message: str):
    base_hash = os.getenv("WRITER_SECRET_KEY")
    if not base_hash:
        raise ValueError("Environment variable WRITER_SECRET_KEY needs to be set up in" + \
                            "order to enable operations which require hash generation, such as creating async jobs.")
    assert HASH_SALT
    combined = base_hash + HASH_SALT + message
    return hashlib.sha256(combined.encode()).hexdigest()

def verify_message_authorization_signature(message: str, request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized. Token not specified.")
    if auth_header != f"Bearer {get_hash(message)}":
        raise HTTPException(status_code=403, detail="Forbidden. Incorrect token.")