Instructions

Project Requirements Document

Title: Automated Load Testing Framework with Locust

1. Objectives

Develop an automated load testing framework powered by Locust.

Dynamically generate test cases based on OpenAPI reference documentation.

Integrate seamlessly into the AWS pipeline for automated execution during CI/CD.

Allow developers to run tests locally for manual validation and debugging.

Provide developers with a submodule tool to prevent performance issues caused by sudden spikes in resource usage.

Ensure system scalability, reliability, and resilience through continuous load validation.

2. Scope

In-Scope:

Implementation of a Locust-based testing framework.

Scraper functionality to generate test cases from OpenAPI specifications.

Integration with AWS CI/CD pipeline.

Support for local execution by developers.

Reporting on performance, latency, and resource utilization.

Reusability as a submodule in different projects.

Out-of-Scope:

Manual performance testing processes outside of the provided framework.

Testing of third-party APIs not documented in OpenAPI specs.

Monitoring/alerting integration (to be handled by existing AWS monitoring tools).

3. Architecture Overview

Scraper Module

Parses OpenAPI specifications.

Auto-generates test endpoints, payloads, and expected behaviors.

Locust Load Testing Core

Simulates concurrent users and traffic patterns.

Configurable load profiles (ramp-up, stress, endurance).

Collects response metrics and error rates.

Can be executed locally by developers or in CI/CD.

AWS Integration

Executes tests as part of CI/CD pipeline.

Stores results in S3 or CloudWatch for reporting.

Supports thresholds for automated pass/fail criteria.

Developer Submodule

Packaged for easy inclusion in other projects.

Provides reusable test templates and configuration options.

Supports both automated and local/manual runs.

4. Deliverables

Codebase: Locust-based testing framework with scraper module.

AWS Pipeline Integration: Automated load testing in CI/CD.

Local Execution Support: CLI or configuration options for developers to run tests manually.

Documentation:

Developer guide for integrating the submodule.

Configuration instructions for test customization.

Instructions for running tests locally.

Reporting and troubleshooting guide.

Demo/Test Report: Initial load test results with performance baselines.

5. Success Criteria

Framework runs automatically in AWS pipeline.

Tests are generated dynamically from OpenAPI specs.

Developers can include the submodule in their projects with minimal setup.

Developers can run manual load tests locally when needed.

Load tests provide clear, actionable reports on performance risks.

System can handle significant spikes in resource usage without failures.


# Project blueprint

## Goals (TL;DR)

* **Locust** tests that **fetch an OpenAPI spec** and **auto-build requests**.
* **Auth**: either pass a **JWT** directly or **log in** (username/password) to obtain one automatically.
* **One Dockerfile + one docker-compose.yml**. Volumes for local dev. Web UI available in dev.
* **Reports** (HTML/CSV/JSON) written to a **mapped path** for easy access.
* First target: **one app**, **≤ 100 concurrent users**; architecture ready for multi-service in the future.

---

## Suggested file tree

```
.
├─ locustfile.py
├─ openapi_loader.py
├─ scenario_builder.py
├─ auth.py
├─ settings.py
├─ utils.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ README.md
├─ .env.example
├─ configs/
│  └─ config.yaml
├─ specs/
│  └─ (optional local OpenAPI files if not using URL)
└─ reports/   (mapped volume; output here)
```

---

## Environment & image parameters (document all in README.md)

These map 1:1 to `docker-compose.yml` (and to CI example step). Keep names short & clear.

| Variable            | Required                 | Example                                | Purpose                                         |
| ------------------- | ------------------------ | -------------------------------------- | ----------------------------------------------- |
| `OPENAPI_URL`       | yes (or `OPENAPI_PATH`)  | `https://api.example.com/openapi.json` | Where to fetch the spec (curl/HTTP)             |
| `OPENAPI_PATH`      | alternative              | `/app/specs/openapi.json`              | Use a local file instead of URL                 |
| `BASE_URL`          | yes                      | `https://staging.example.com`          | Target base URL for requests                    |
| `AUTH_MODE`         | no                       | `jwt` or `login`                       | Choose between direct JWT or login flow         |
| `JWT_TOKEN`         | req if `AUTH_MODE=jwt`   | `eyJhbGci...`                          | Bearer token to use                             |
| `LOGIN_URL`         | req if `AUTH_MODE=login` | `/auth/login`                          | Relative or absolute login endpoint             |
| `LOGIN_USER`        | req if `AUTH_MODE=login` | `tester@example.com`                   | Username/email                                  |
| `LOGIN_PASS`        | req if `AUTH_MODE=login` | `s3cret`                               | Password                                        |
| `SPEC_INCLUDE_TAGS` | no                       | `users,orders`                         | Comma list to **include** only tagged endpoints |
| `SPEC_EXCLUDE_TAGS` | no                       | `admin`                                | Comma list to **exclude** tags                  |
| `MAX_USERS`         | no                       | `100`                                  | Safety cap; default 100                         |
| `SPAWN_RATE`        | no                       | `5`                                    | Users/sec ramp rate                             |
| `RUN_TIME`          | no                       | `10m`                                  | (Optional) for headless CI runs                 |
| `REQUEST_TIMEOUT`   | no                       | `10`                                   | Seconds per request                             |
| `RETRY_COUNT`       | no                       | `1`                                    | Simple retry for 5xx/timeout                    |
| `REPORTS_DIR`       | no                       | `/app/reports`                         | Where reports are written                       |
| `LOCUST_HOST`       | derived                  | `BASE_URL`                             | Locust’s host (we’ll set it automatically)      |
| `EXTRA_HEADERS`     | no                       | `{"X-Env":"staging"}`                  | Additional headers JSON                         |

> All of the above should be **fully explained** in `README.md` with examples.

`.env.example` (copy to `.env` for local dev):

```env
OPENAPI_URL=https://staging.example.com/openapi.json
BASE_URL=https://staging.example.com
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=locust
LOGIN_PASS=locustpass
MAX_USERS=100
SPAWN_RATE=5
RUN_TIME=10m
REPORTS_DIR=/app/reports
REQUEST_TIMEOUT=10
RETRY_COUNT=1
SPEC_INCLUDE_TAGS=public,orders
SPEC_EXCLUDE_TAGS=admin
EXTRA_HEADERS={"X-Env":"staging"}
```

---

## Core modules

### `auth.py`

```python
import os, json, requests

def get_auth_headers():
    mode = os.getenv("AUTH_MODE", "").lower()
    extra = os.getenv("EXTRA_HEADERS")
    extra_headers = {}
    if extra:
        try:
            extra_headers = json.loads(extra)
        except Exception:
            pass

    if mode == "jwt":
        token = os.getenv("JWT_TOKEN")
        if not token:
            raise RuntimeError("AUTH_MODE=jwt but JWT_TOKEN not provided")
        return {"Authorization": f"Bearer {token}", **extra_headers}

    if mode == "login":
        base = os.getenv("BASE_URL")
        login_url = os.getenv("LOGIN_URL")
        user = os.getenv("LOGIN_USER")
        pwd = os.getenv("LOGIN_PASS")
        if not all([base, login_url, user, pwd]):
            raise RuntimeError("AUTH_MODE=login requires BASE_URL, LOGIN_URL, LOGIN_USER, LOGIN_PASS")
        url = login_url if login_url.startswith("http") else f"{base.rstrip('/')}/{login_url.lstrip('/')}"
        resp = requests.post(url, json={"username": user, "password": pwd}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        token = data.get("access_token") or data.get("token") or data.get("jwt")
        if not token:
            raise RuntimeError("Login succeeded but no token found in response")
        return {"Authorization": f"Bearer {token}", **extra_headers}

    # No auth
    return {**extra_headers}
```

### `openapi_loader.py`

```python
import os, requests, json

def load_openapi():
    path = os.getenv("OPENAPI_PATH")
    url  = os.getenv("OPENAPI_URL")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    if url:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Provide OPENAPI_URL or OPENAPI_PATH")
```

### `scenario_builder.py`

```python
import os, random, re
from urllib.parse import urljoin

# Minimal helpers to convert OpenAPI schemas into sample payloads.
def sample_from_schema(schema):
    if not schema:
        return None
    t = schema.get("type")
    if t == "string":
        fmt = schema.get("format")
        if fmt == "email": return "user@example.com"
        if fmt == "date-time": return "2020-01-01T00:00:00Z"
        return schema.get("example") or "string"
    if t == "integer": return schema.get("example") or 1
    if t == "number": return schema.get("example") or 1.0
    if t == "boolean": return schema.get("example") or True
    if t == "array": return [sample_from_schema(schema.get("items"))]
    if t == "object":
        props = schema.get("properties", {})
        return {k: sample_from_schema(v) for k,v in props.items()}
    return schema.get("example")

def build_tasks(spec, include_tags=None, exclude_tags=None):
    include = set([t.strip() for t in (include_tags or "").split(",") if t.strip()])
    exclude = set([t.strip() for t in (exclude_tags or "").split(",") if t.strip()])
    paths = spec.get("paths", {})
    tasks = []
    for pth, ops in paths.items():
        for method, op in ops.items():
            if method.lower() not in {"get","post","put","patch","delete"}: 
                continue
            tags = set(op.get("tags", []))
            if include and not (tags & include): 
                continue
            if exclude and (tags & exclude):
                continue

            # Build payload if requestBody is present
            payload = None
            if "requestBody" in op:
                content = op["requestBody"].get("content", {})
                app_json = content.get("application/json")
                if app_json and "schema" in app_json:
                    payload = sample_from_schema(app_json["schema"])

            # Path/query parameters (very basic examples)
            params = op.get("parameters", [])
            path_params = {}
            query_params = {}
            for prm in params:
                name = prm.get("name")
                loc  = prm.get("in")
                schema = prm.get("schema", {})
                val = sample_from_schema(schema)
                if loc == "path":
                    path_params[name] = val
                elif loc == "query":
                    query_params[name] = val

            tasks.append({
                "method": method.upper(),
                "path": pth,
                "path_params": path_params,
                "query_params": query_params,
                "payload": payload
            })
    return tasks
```

### `settings.py`

```python
import os, json

MAX_USERS = int(os.getenv("MAX_USERS", "100"))
SPAWN_RATE = float(os.getenv("SPAWN_RATE", "5"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
RETRY_COUNT = int(os.getenv("RETRY_COUNT", "1"))
REPORTS_DIR = os.getenv("REPORTS_DIR", "/app/reports")
SPEC_INCLUDE_TAGS = os.getenv("SPEC_INCLUDE_TAGS", "")
SPEC_EXCLUDE_TAGS = os.getenv("SPEC_EXCLUDE_TAGS", "")

def extra_headers():
    raw = os.getenv("EXTRA_HEADERS")
    if not raw: return {}
    try: return json.loads(raw)
    except Exception: return {}
```

### `locustfile.py`

```python
import os, time, random
from locust import HttpUser, task, between, events
from requests.exceptions import RequestException
from auth import get_auth_headers
from openapi_loader import load_openapi
from scenario_builder import build_tasks
from settings import REQUEST_TIMEOUT, RETRY_COUNT, SPEC_INCLUDE_TAGS, SPEC_EXCLUDE_TAGS

SPEC = load_openapi()
TASKS = build_tasks(SPEC, SPEC_INCLUDE_TAGS, SPEC_EXCLUDE_TAGS)
AUTH_HEADERS = None

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global AUTH_HEADERS
    AUTH_HEADERS = get_auth_headers()
    base = os.getenv("BASE_URL")
    if base:
        environment.host = base  # Set Locust host dynamically

class OpenApiUser(HttpUser):
    wait_time = between(0.5, 2.5)

    @task
    def dynamic_endpoints(self):
        if not TASKS:
            return
        t = random.choice(TASKS)
        path = t["path"]
        # Fill path params like /users/{id}
        for k, v in (t["path_params"] or {}).items():
            path = path.replace("{"+k+"}", str(v))

        # Basic retry loop
        last_exc = None
        for _ in range(max(RETRY_COUNT,1)):
            try:
                if t["method"] == "GET":
                    with self.client.get(
                        path,
                        headers=AUTH_HEADERS,
                        params=t["query_params"],
                        name=f"{t['method']} {t['path']}",
                        timeout=REQUEST_TIMEOUT,
                        catch_response=True
                    ) as resp:
                        if resp.status_code >= 500:
                            resp.failure(f"Server error {resp.status_code}")
                        else:
                            resp.success()
                    return
                else:
                    with self.client.request(
                        t["method"],
                        path,
                        headers=AUTH_HEADERS,
                        params=t["query_params"],
                        json=t["payload"],
                        name=f"{t['method']} {t['path']}",
                        timeout=REQUEST_TIMEOUT,
                        catch_response=True
                    ) as resp:
                        if resp.status_code >= 500:
                            resp.failure(f"Server error {resp.status_code}")
                        else:
                            resp.success()
                    return
            except RequestException as e:
                last_exc = e
                time.sleep(0.2)
        if last_exc:
            # This will show up in Locust failures
            raise last_exc
```

---

## Docker & Compose

### `requirements.txt`

```
locust>=2.30.0
requests>=2.32.0
pyyaml>=6.0.2
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System deps (curl for debugging, optional)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Reports dir
RUN mkdir -p /app/reports

# Default: Locust web UI on port 8089 for dev
EXPOSE 8089

# Entrypoint supports headless or UI depending on env
ENTRYPOINT ["bash", "-lc", "if [ -n \"$RUN_TIME\" ]; then \
  locust -f locustfile.py --headless -u ${MAX_USERS:-100} -r ${SPAWN_RATE:-5} --run-time ${RUN_TIME} --csv=/app/reports/results --html /app/reports/report.html; \
else \
  locust -f locustfile.py --web-host=0.0.0.0 --web-port=8089; \
fi"]
```

### `docker-compose.yml`

```yaml
version: "3.9"
services:
  locust:
    build: .
    env_file:
      - .env
    environment:
      # fallbacks if .env not present
      - REPORTS_DIR=/app/reports
    ports:
      - "8089:8089"   # Locust web UI in dev
    volumes:
      - ./reports:/app/reports
      - ./specs:/app/specs
      - ./:/app       # optional: hot-reload python for dev convenience
    restart: unless-stopped
```

> In dev, open **[http://localhost:8089](http://localhost:8089)** for the Locust web UI.
> Reports (HTML/CSV) appear under `./reports`.

---

## How to run

### Local (dev, with web UI)

```bash
cp .env.example .env
docker compose up --build
# open http://localhost:8089
# set users (≤ MAX_USERS), spawn rate, and start
```

### Local headless (generates reports automatically)

```bash
RUN_TIME=10m MAX_USERS=100 SPAWN_RATE=5 docker compose run --rm locust
# Reports -> ./reports/report.html and ./reports/results_*.csv
```

---

## CI/CD example step (containerized, staging target)

We’re not building the whole pipeline—just an example step. Replace with your runner syntax.

**GitHub Actions (example):**

```yaml
- name: Run Locust (staging)
  uses: docker://ghcr.io/your-org/locust-openapi:latest
  env:
    OPENAPI_URL: https://staging.example.com/openapi.json
    BASE_URL: https://staging.example.com
    AUTH_MODE: login
    LOGIN_URL: /auth/login
    LOGIN_USER: ${{ secrets.LOGIN_USER }}
    LOGIN_PASS: ${{ secrets.LOGIN_PASS }}
    MAX_USERS: "100"
    SPAWN_RATE: "5"
    RUN_TIME: "10m"
    REPORTS_DIR: /app/reports
  with:
    args: ""
  continue-on-error: false
```

Archive the `reports/` directory as an artifact in your pipeline.

---

## Emulating **miscellaneous scenarios**

You can do all of these from the Locust UI or as env vars in headless mode:

1. **Ramp-up** (gradual increase)

   * Use `SPAWN_RATE=5`, `MAX_USERS=100`.
   * In UI: set Users to 100, Spawn rate to 5.

2. **Spike** (sudden surge)

   * Start at 10 users, then quickly ramp to 100 (UI lets you change users on the fly).
   * Or headless: first run with `MAX_USERS=10`, then a short second run with `MAX_USERS=100` and `SPAWN_RATE=100`.

3. **Soak** (steady long run)

   * `RUN_TIME=2h`, `MAX_USERS=50`, `SPAWN_RATE=2`.
   * Validates memory leaks / slow degradation.

4. **Error paths / 4xx/5xx resilience**

   * Use `SPEC_INCLUDE_TAGS` to focus on brittle endpoints.
   * Temporarily inject invalid query params through a small tweak in `scenario_builder.py` (e.g., 10% of the time).

5. **Data-dependent flows**

   * Extend `scenario_builder.py` to chain operations: create → read → update → delete using IDs returned by previous steps.

6. **Multi-env comparison**

   * Run the same `RUN_TIME`, `MAX_USERS`, `SPAWN_RATE` against `BASE_URL=staging` and `BASE_URL=dev` to compare baseline vs. new build.

> Because the tests are built from the spec, you can **include/exclude tags** to tailor scenarios without editing code.

---

## Reporting

* **HTML report**: `reports/report.html`
* **CSV** (requests, failures, distribution): `reports/results_requests.csv`, etc.
* In CI, upload `reports/` as an artifact.
* If desired later: push metrics to S3/CloudWatch (kept out of scope for now).

---

## Notes on simplicity & future-proofing

* Single **Dockerfile** and **docker-compose.yml**, volumes mapped for:

  * `/app/reports` → `./reports`
  * `/app/specs` → `./specs`
  * `./` → `/app` (optional but handy for editing Python live in dev)
* First target: **one app / ≤ 100 users**; the dynamic builder makes it straightforward to add a second OpenAPI spec (multi-tool) by:

  * Adding a second service in `docker-compose.yml` pointing at a different `.env` or `OPENAPI_URL`
  * Or looping across multiple specs in the same container run (future enhancement).

---

## What I can add next (if you want)

* A polished **README.md** (copy-paste ready) with quickstart, parameter table, examples, and troubleshooting.
* Optional **thresholds** (fail the run if P95 latency/error rate exceeds a value).
* Tag-aware **scenario weights** (e.g., hit “orders” 3x more than “users”).

If this structure works for you, I’ll write the **README.md** and add a tiny thresholds helper next.

