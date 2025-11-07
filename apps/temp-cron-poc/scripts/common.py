from dataclasses import dataclass

BASE_URL = "http://127.0.0.1:5000/private/api"
TEMPORAL_SERVER_URL = "localhost:7233"

@dataclass
class JobParams:
    blueprint_id: str
    branch_id: str