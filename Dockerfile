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