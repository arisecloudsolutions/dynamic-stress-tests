import os
import json

MAX_USERS = int(os.getenv("MAX_USERS", "100"))
SPAWN_RATE = float(os.getenv("SPAWN_RATE", "5"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
RETRY_COUNT = int(os.getenv("RETRY_COUNT", "1"))
REPORTS_DIR = os.getenv("REPORTS_DIR", "/mnt/locust/reports")
SPEC_INCLUDE_TAGS = os.getenv("SPEC_INCLUDE_TAGS", "")
SPEC_EXCLUDE_TAGS = os.getenv("SPEC_EXCLUDE_TAGS", "")

def extra_headers():
    raw = os.getenv("EXTRA_HEADERS")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}