FROM locustio/locust

WORKDIR /mnt/locust

# Install additional dependencies for OpenAPI processing
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ .

# Create reports directory
RUN mkdir -p /mnt/locust/reports

# Expose Locust web UI port
EXPOSE 8089

# Dynamic entrypoint based on environment
ENTRYPOINT ["sh", "-c", "if [ -n \"$RUN_TIME\" ]; then \
  locust -f locustfile.py --headless -u ${MAX_USERS:-100} -r ${SPAWN_RATE:-5} --run-time ${RUN_TIME} --csv=/mnt/locust/reports/results --html /mnt/locust/reports/report.html --host=${BASE_URL}; \
else \
  locust -f locustfile.py --web-host=0.0.0.0 --web-port=8089 --host=${BASE_URL}; \
fi"]