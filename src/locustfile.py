import os
import time
import random
import logging
from typing import Dict, Any, List, Optional

from locust import HttpUser, task, between, events
from locust.exception import StopUser
from requests.exceptions import RequestException

# Import our custom modules
from openapi_loader import OpenAPILoader
from scenario_builder import ScenarioBuilder
from auth import AuthenticationManager
from utils import (
    LoadTestReporter,
    EnvironmentValidator,
    EndpointHealthChecker,
    setup_logging,
    save_json_report
)
from settings import (
    REQUEST_TIMEOUT,
    RETRY_COUNT,
    SPEC_INCLUDE_TAGS,
    SPEC_EXCLUDE_TAGS
)

# Global variables for sharing data between Locust instances
OPENAPI_SPEC: Optional[Dict[str, Any]] = None
TEST_TASKS: List[Dict[str, Any]] = []
AUTH_MANAGER: Optional[AuthenticationManager] = None
REPORTER: Optional[LoadTestReporter] = None
STARTUP_ERRORS: List[str] = []

def initialize_test_environment():
    """
    Initialize the test environment by loading OpenAPI spec,
    building scenarios, and validating configuration.
    """
    global OPENAPI_SPEC, TEST_TASKS, AUTH_MANAGER, REPORTER, STARTUP_ERRORS

    try:
        print("\n" + "="*60)
        print(" INITIALIZING DYNAMIC STRESS TEST FRAMEWORK")
        print("="*60)

        # Setup logging
        setup_logging()

        # Validate environment configuration
        print("1️⃣  Validating configuration...")
        validation_errors = EnvironmentValidator.validate_configuration()
        if validation_errors:
            STARTUP_ERRORS.extend(validation_errors)
            for error in validation_errors:
                print(f"   {error}")
            return False

        EnvironmentValidator.print_configuration_summary()

        # Initialize authentication
        print("\n2️⃣  Initializing authentication...")
        AUTH_MANAGER = AuthenticationManager()
        auth_headers = AUTH_MANAGER.get_auth_headers()
        print("✅ Authentication configured successfully")

        # Load OpenAPI specification
        print("\n3️⃣  Loading OpenAPI specification...")
        loader = OpenAPILoader()
        OPENAPI_SPEC = loader.load_openapi()

        # Build test scenarios
        print("\n4️⃣  Building test scenarios...")
        builder = ScenarioBuilder(OPENAPI_SPEC)
        TEST_TASKS = builder.build_tasks(SPEC_INCLUDE_TAGS, SPEC_EXCLUDE_TAGS)

        if not TEST_TASKS:
            error = "💀 No test scenarios generated. Check your tag filters or OpenAPI spec."
            STARTUP_ERRORS.append(error)
            print(error)
            return False

        # Initialize reporter
        REPORTER = LoadTestReporter()

        # Health check
        print("\n5️⃣  Performing health checks...")
        base_url = os.getenv("BASE_URL", "")
        health_checker = EndpointHealthChecker(base_url, auth_headers)

        if not health_checker.check_base_connectivity():
            error = f"💀 Cannot connect to base URL: {base_url}"
            STARTUP_ERRORS.append(error)
            print(error)
            return False

        # Sample endpoint check
        health_results = health_checker.sample_endpoint_check(TEST_TASKS, max_checks=5)
        if health_results["checked"] > 0 and health_results["accessible"] == 0:
            error = "💀 No sample endpoints are accessible"
            STARTUP_ERRORS.append(error)
            print(error)
            return False

        print("\n" + "="*60)
        print("✅ FRAMEWORK INITIALIZATION COMPLETE")
        print(f"   📊 {len(TEST_TASKS)} test scenarios ready")
        print(f"   🎯 Target: {base_url}")
        print(f"   🔐 Auth: {os.getenv('AUTH_MODE', 'none').upper()}")
        print("="*60 + "\n")

        # Save initialization report
        init_report = {
            "initialization": {
                "timestamp": time.time(),
                "base_url": base_url,
                "auth_mode": os.getenv('AUTH_MODE', 'none'),
                "total_scenarios": len(TEST_TASKS),
                "health_check": health_results,
                "openapi_source": loader.source,
                "validation_results": loader.validation_results
            },
            "scenarios": TEST_TASKS,
            "endpoint_summary": loader.get_endpoint_summary()
        }
        save_json_report(init_report, "test_initialization.json")

        return True

    except Exception as e:
        error = f"💀 Initialization failed: {str(e)}"
        STARTUP_ERRORS.append(error)
        print(error)
        logging.exception("Initialization failed")
        return False


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Event handler called when test starts.
    Initializes the test environment and sets Locust host.
    """
    global STARTUP_ERRORS

    print("🎬 Test starting...")

    # Initialize test environment
    if not initialize_test_environment():
        print("\n💀 TEST INITIALIZATION FAILED")
        print("Startup errors:")
        for error in STARTUP_ERRORS:
            print(f"   {error}")
        print("\n💡 Please fix the errors above and restart the test.")
        # Don't stop the test here, let individual users handle the error
        return

    # Set Locust host dynamically
    base_url = os.getenv("BASE_URL")
    if base_url and environment.host != base_url:
        print(f"🎯 Setting Locust host to: {base_url}")
        environment.host = base_url


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Event handler called when test stops.
    Generates final report and saves results.
    """
    global REPORTER

    print("\n🏁 Test stopping...")

    if REPORTER:
        # Generate final report
        final_report = REPORTER.generate_final_report()

        # Print summary
        summary = final_report["summary"]
        print("\n" + "="*60)
        print("📊 FINAL TEST REPORT")
        print("="*60)
        print(f"⏱️  Duration: {summary['test_duration']:.1f}s")
        print(f"📈 Total Requests: {summary['total_requests']}")
        print(f"💀 Total Failures: {summary['total_failures']} ({summary['failure_rate']:.1f}%)")
        print(f"⚡ Requests/sec: {summary['requests_per_second']:.1f}")

        # Performance metrics
        if "performance_metrics" in final_report and final_report["performance_metrics"]:
            metrics = final_report["performance_metrics"]
            percentiles = metrics.get("response_time_percentiles", {})
            print(f"\n⏱️  Response Times:")
            print(f"   Average: {metrics.get('avg_response_time', 0):.1f}ms")
            print(f"   P50: {percentiles.get('p50', 0):.1f}ms")
            print(f"   P95: {percentiles.get('p95', 0):.1f}ms")
            print(f"   P99: {percentiles.get('p99', 0):.1f}ms")

        # Top errors
        if final_report["errors"]:
            print(f"\n💀 Top Errors:")
            sorted_errors = sorted(final_report["errors"].items(), key=lambda x: x[1], reverse=True)
            for error, count in sorted_errors[:5]:
                print(f"   {error}: {count} occurrences")

        print("="*60)

        # Save detailed report
        save_json_report(final_report, "final_test_report.json")
        print("📄 Detailed reports saved to reports/ directory")


class DynamicAPIUser(HttpUser):
    """
    Locust user class that dynamically tests API endpoints based on OpenAPI specification.
    """

    wait_time = between(0.5, 2.5)  # Wait between requests

    def on_start(self):
        """Called when a user starts. Check if initialization was successful."""
        global STARTUP_ERRORS, TEST_TASKS, AUTH_MANAGER

        if STARTUP_ERRORS:
            print(f"💀 User cannot start due to initialization errors: {STARTUP_ERRORS}")
            raise StopUser()

        if not TEST_TASKS:
            print("💀 No test tasks available")
            raise StopUser()

        if not AUTH_MANAGER:
            print("💀 Authentication manager not initialized")
            raise StopUser()

        print(f"👤 User {self.environment.runner.user_count} started")

    @task
    def execute_dynamic_api_test(self):
        """
        Main task that selects and executes a random API endpoint test.
        This is where the magic happens - dynamic API testing!
        """
        global TEST_TASKS, AUTH_MANAGER, REPORTER

        if not TEST_TASKS or not AUTH_MANAGER:
            return

        # Select a weighted random task
        task = self._select_weighted_task()
        if not task:
            return

        # Get current auth headers (handles token refresh if needed)
        try:
            auth_headers = AUTH_MANAGER.get_auth_headers()
        except Exception as e:
            print(f"💀 Authentication failed: {e}")
            return

        # Execute the API call
        self._execute_api_task(task, auth_headers)

    def _select_weighted_task(self) -> Optional[Dict[str, Any]]:
        """Select a task based on weights."""
        if not TEST_TASKS:
            return None

        # Simple weighted selection
        total_weight = sum(task.get("weight", 1) for task in TEST_TASKS)
        if total_weight == 0:
            return random.choice(TEST_TASKS)

        random_weight = random.uniform(0, total_weight)
        current_weight = 0

        for task in TEST_TASKS:
            current_weight += task.get("weight", 1)
            if random_weight <= current_weight:
                return task

        return TEST_TASKS[-1]  # Fallback

    def _execute_api_task(self, task: Dict[str, Any], auth_headers: Dict[str, str]):
        """Execute a single API task with retries and error handling."""
        method = task["method"]
        path = task["path"]

        # Build the request URL with path parameters
        request_path = self._build_request_path(task)

        # Prepare request data
        query_params = task.get("query_params", {})
        request_body = task.get("request_body")
        additional_headers = task.get("header_params", {})

        # Merge headers
        headers = {**auth_headers, **additional_headers}

        # Request name for Locust statistics
        request_name = f"{method} {path}"

        # Retry logic
        last_exception = None
        for attempt in range(max(1, RETRY_COUNT)):
            try:
                start_time = time.time()

                # Make the request using Locust's client
                with self.client.request(
                    method=method,
                    url=request_path,
                    params=query_params if method == "GET" else None,
                    json=request_body if method in ["POST", "PUT", "PATCH"] and request_body else None,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                    name=request_name,
                    catch_response=True
                ) as response:

                    response_time = (time.time() - start_time) * 1000  # Convert to ms

                    # Log the request for reporting
                    if REPORTER:
                        error_msg = None
                        if response.status_code >= 400:
                            error_msg = f"HTTP {response.status_code}"
                        REPORTER.log_request(method, path, response_time, response.status_code, error_msg)

                    # Handle response
                    if response.status_code >= 500:
                        response.failure(f"Server error: HTTP {response.status_code}")
                    elif response.status_code >= 400:
                        # Client errors are often expected in API testing
                        response.success()  # Don't count as failures for 4xx
                    else:
                        response.success()

                    return  # Success, exit retry loop

            except RequestException as e:
                last_exception = e
                response_time = (time.time() - start_time) * 1000

                # Log failed request
                if REPORTER:
                    REPORTER.log_request(method, path, response_time, 0, str(e))

                if attempt < RETRY_COUNT - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    # Final attempt failed
                    self.client.get(
                        request_path,
                        name=request_name,
                        catch_response=True
                    ).failure(f"Request failed after {RETRY_COUNT} attempts: {str(e)}")

            except Exception as e:
                # Unexpected error
                logging.exception(f"Unexpected error in API task: {e}")
                if REPORTER:
                    REPORTER.log_request(method, path, 0, 0, f"Unexpected error: {str(e)}")
                break

    def _build_request_path(self, task: Dict[str, Any]) -> str:
        """Build the complete request path with path parameters filled in."""
        path = task["path"]
        path_params = task.get("path_params", {})

        # Replace path parameters like {id} with actual values
        for param_name, param_value in path_params.items():
            placeholder = f"{{{param_name}}}"
            if placeholder in path:
                path = path.replace(placeholder, str(param_value))

        return path

    @task(1)  # Lower weight task
    def print_live_statistics(self):
        """Periodically print live statistics (lower frequency)."""
        global REPORTER

        if REPORTER and random.random() < 0.1:  # Only 10% chance to run
            REPORTER.print_live_stats()


# Performance monitoring events
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Log individual requests for monitoring."""
    # This event is automatically handled by Locust
    # Additional custom monitoring can be added here if needed
    pass


if __name__ == "__main__":
    # This allows testing the locustfile directly
    print("🧪 Testing locustfile module...")

    # Set test environment
    os.environ.update({
        "OPENAPI_URL": "https://petstore3.swagger.io/api/v3/openapi.json",
        "BASE_URL": "https://petstore3.swagger.io/api/v3",
        "AUTH_MODE": "none",
        "MAX_USERS": "10",
        "SPAWN_RATE": "2"
    })

    success = initialize_test_environment()
    if success:
        print(f"✅ Test environment initialized with {len(TEST_TASKS)} tasks")
        print("Ready to run with: locust -f locustfile.py")
    else:
        print("💀 Test environment initialization failed")
        for error in STARTUP_ERRORS:
            print(f"   {error}")