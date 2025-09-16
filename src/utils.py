import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from urllib.parse import urljoin

class LoadTestReporter:
    """
    Provides comprehensive reporting and visualization for load test results.
    Generates summaries, metrics, and visual feedback for developers.
    """

    def __init__(self):
        self.start_time = time.time()
        self.test_results = []
        self.endpoint_stats = {}
        self.error_summary = {}

    def log_request(self, method: str, path: str, response_time: float, status_code: int, error: Optional[str] = None):
        """Log individual request results for analysis."""
        endpoint_key = f"{method} {path}"

        # Update endpoint statistics
        if endpoint_key not in self.endpoint_stats:
            self.endpoint_stats[endpoint_key] = {
                "requests": 0,
                "failures": 0,
                "total_response_time": 0,
                "min_response_time": float('inf'),
                "max_response_time": 0,
                "status_codes": {}
            }

        stats = self.endpoint_stats[endpoint_key]
        stats["requests"] += 1
        stats["total_response_time"] += response_time
        stats["min_response_time"] = min(stats["min_response_time"], response_time)
        stats["max_response_time"] = max(stats["max_response_time"], response_time)

        # Track status codes
        stats["status_codes"][status_code] = stats["status_codes"].get(status_code, 0) + 1

        # Track failures
        if error or status_code >= 400:
            stats["failures"] += 1
            error_key = f"{status_code}: {error or 'HTTP Error'}"
            self.error_summary[error_key] = self.error_summary.get(error_key, 0) + 1

    def print_live_stats(self):
        """Print real-time statistics during test execution."""
        runtime = time.time() - self.start_time
        total_requests = sum(stats["requests"] for stats in self.endpoint_stats.values())
        total_failures = sum(stats["failures"] for stats in self.endpoint_stats.values())

        if total_requests == 0:
            return

        print(f"\n📊 LIVE STATS (Runtime: {runtime:.1f}s)")
        print("-" * 50)
        print(f"Total Requests: {total_requests}")
        print(f"Total Failures: {total_failures} ({(total_failures/total_requests)*100:.1f}%)")
        print(f"RPS: {total_requests/runtime:.1f}")

        # Top endpoints by volume
        top_endpoints = sorted(
            self.endpoint_stats.items(),
            key=lambda x: x[1]["requests"],
            reverse=True
        )[:5]

        print("\n🎯 TOP ENDPOINTS:")
        for endpoint, stats in top_endpoints:
            avg_time = stats["total_response_time"] / stats["requests"]
            failure_rate = (stats["failures"] / stats["requests"]) * 100
            print(f"  {endpoint:30} | {stats['requests']:4d} req | {avg_time:6.1f}ms avg | {failure_rate:4.1f}% fail")

    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final test report."""
        runtime = time.time() - self.start_time
        total_requests = sum(stats["requests"] for stats in self.endpoint_stats.values())
        total_failures = sum(stats["failures"] for stats in self.endpoint_stats.values())

        report = {
            "summary": {
                "test_duration": runtime,
                "total_requests": total_requests,
                "total_failures": total_failures,
                "failure_rate": (total_failures / total_requests * 100) if total_requests > 0 else 0,
                "requests_per_second": total_requests / runtime if runtime > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "endpoints": {},
            "errors": self.error_summary,
            "performance_metrics": self._calculate_performance_metrics()
        }

        # Detailed endpoint analysis
        for endpoint, stats in self.endpoint_stats.items():
            if stats["requests"] > 0:
                avg_response_time = stats["total_response_time"] / stats["requests"]
                report["endpoints"][endpoint] = {
                    "requests": stats["requests"],
                    "failures": stats["failures"],
                    "failure_rate": (stats["failures"] / stats["requests"]) * 100,
                    "avg_response_time": avg_response_time,
                    "min_response_time": stats["min_response_time"],
                    "max_response_time": stats["max_response_time"],
                    "status_codes": stats["status_codes"]
                }

        return report

    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        all_response_times = []
        for stats in self.endpoint_stats.values():
            if stats["requests"] > 0:
                avg_time = stats["total_response_time"] / stats["requests"]
                all_response_times.extend([avg_time] * stats["requests"])

        if not all_response_times:
            return {}

        all_response_times.sort()
        length = len(all_response_times)

        return {
            "response_time_percentiles": {
                "p50": all_response_times[int(length * 0.5)] if length > 0 else 0,
                "p90": all_response_times[int(length * 0.9)] if length > 0 else 0,
                "p95": all_response_times[int(length * 0.95)] if length > 0 else 0,
                "p99": all_response_times[int(length * 0.99)] if length > 0 else 0
            },
            "avg_response_time": sum(all_response_times) / length,
            "min_response_time": min(all_response_times),
            "max_response_time": max(all_response_times)
        }


class EnvironmentValidator:
    """
    Validates environment configuration and provides helpful error messages.
    """

    @staticmethod
    def validate_configuration() -> List[str]:
        """
        Validate all environment configuration.

        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []

        # Validate OpenAPI source
        openapi_url = os.getenv("OPENAPI_URL")
        openapi_path = os.getenv("OPENAPI_PATH")

        if not openapi_url and not openapi_path:
            errors.append("💀 Either OPENAPI_URL or OPENAPI_PATH must be set")
        elif openapi_path and not os.path.exists(openapi_path):
            errors.append(f"💀 OPENAPI_PATH file does not exist: {openapi_path}")

        # Validate base URL
        base_url = os.getenv("BASE_URL")
        if not base_url:
            errors.append("💀 BASE_URL is required")
        elif not base_url.startswith(("http://", "https://")):
            errors.append("💀 BASE_URL must start with http:// or https://")

        # Validate authentication configuration
        auth_mode = os.getenv("AUTH_MODE", "").lower()
        if auth_mode:
            auth_errors = EnvironmentValidator._validate_auth_config(auth_mode)
            errors.extend(auth_errors)

        # Validate numeric settings
        numeric_settings = {
            "MAX_USERS": (1, 10000),
            "SPAWN_RATE": (0.1, 1000),
            "REQUEST_TIMEOUT": (1, 300),
            "RETRY_COUNT": (0, 10)
        }

        for setting, (min_val, max_val) in numeric_settings.items():
            value_str = os.getenv(setting)
            if value_str:
                try:
                    value = float(value_str)
                    if not min_val <= value <= max_val:
                        errors.append(f"💀 {setting}={value} is outside valid range [{min_val}, {max_val}]")
                except ValueError:
                    errors.append(f"💀 {setting}='{value_str}' is not a valid number")

        return errors

    @staticmethod
    def _validate_auth_config(auth_mode: str) -> List[str]:
        """Validate authentication-specific configuration."""
        errors = []

        if auth_mode == "jwt":
            if not os.getenv("JWT_TOKEN"):
                errors.append("💀 AUTH_MODE=jwt requires JWT_TOKEN")

        elif auth_mode == "login":
            required_vars = ["LOGIN_URL", "LOGIN_USER", "LOGIN_PASS"]
            for var in required_vars:
                if not os.getenv(var):
                    errors.append(f"💀 AUTH_MODE=login requires {var}")

        elif auth_mode == "apikey":
            if not os.getenv("API_KEY"):
                errors.append("💀 AUTH_MODE=apikey requires API_KEY")

        elif auth_mode == "basic":
            basic_user = os.getenv("BASIC_USER") or os.getenv("LOGIN_USER")
            basic_pass = os.getenv("BASIC_PASS") or os.getenv("LOGIN_PASS")
            if not basic_user or not basic_pass:
                errors.append("💀 AUTH_MODE=basic requires BASIC_USER and BASIC_PASS (or LOGIN_USER and LOGIN_PASS)")

        elif auth_mode == "oauth":
            required_vars = ["OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET", "OAUTH_TOKEN_URL"]
            for var in required_vars:
                if not os.getenv(var):
                    errors.append(f"💀 AUTH_MODE=oauth requires {var}")

        elif auth_mode not in ["", "none"]:
            errors.append(f"💀 Unknown AUTH_MODE: {auth_mode}. Valid options: jwt, login, apikey, basic, oauth")

        return errors

    @staticmethod
    def print_configuration_summary():
        """Print a summary of current configuration."""
        print("\n" + "="*60)
        print("⚙️  CONFIGURATION SUMMARY")
        print("="*60)

        # Core settings
        print(f"🌐 OpenAPI Source: {os.getenv('OPENAPI_URL') or os.getenv('OPENAPI_PATH') or 'NOT SET'}")
        print(f"🎯 Target URL: {os.getenv('BASE_URL', 'NOT SET')}")
        print(f"🔐 Auth Mode: {os.getenv('AUTH_MODE', 'none').upper()}")

        # Load testing settings
        print(f"👥 Max Users: {os.getenv('MAX_USERS', '100')}")
        print(f"⚡ Spawn Rate: {os.getenv('SPAWN_RATE', '5')}/sec")
        print(f"⏱️  Request Timeout: {os.getenv('REQUEST_TIMEOUT', '10')}s")
        print(f"🔄 Retry Count: {os.getenv('RETRY_COUNT', '1')}")

        # Filtering
        include_tags = os.getenv('SPEC_INCLUDE_TAGS', '')
        exclude_tags = os.getenv('SPEC_EXCLUDE_TAGS', '')
        if include_tags:
            print(f"📌 Include Tags: {include_tags}")
        if exclude_tags:
            print(f"🚫 Exclude Tags: {exclude_tags}")

        # Runtime mode
        run_time = os.getenv('RUN_TIME', '')
        if run_time:
            print(f"⏰ Run Time: {run_time} (headless mode)")
        else:
            print("🖥️  Mode: Interactive Web UI")

        print("="*60)


class EndpointHealthChecker:
    """
    Checks endpoint health before starting load tests.
    Provides early feedback on connectivity and authentication issues.
    """

    def __init__(self, base_url: str, auth_headers: Dict[str, str]):
        self.base_url = base_url.rstrip("/")
        self.auth_headers = auth_headers

    def check_base_connectivity(self) -> bool:
        """Check if base URL is accessible."""
        try:
            print(f"🔍 Checking connectivity to {self.base_url}...")
            response = requests.head(self.base_url, timeout=10, headers=self.auth_headers)
            print(f"✅ Base URL accessible (HTTP {response.status_code})")
            return True
        except requests.exceptions.ConnectionError:
            print(f"💀 Cannot connect to {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            print(f"💀 Timeout connecting to {self.base_url}")
            return False
        except Exception as e:
            print(f"⚠️  Connection check failed: {e}")
            return False

    def sample_endpoint_check(self, endpoints: List[Dict[str, Any]], max_checks: int = 3) -> Dict[str, Any]:
        """
        Test a sample of endpoints to verify they're accessible.

        Args:
            endpoints: List of endpoint dictionaries from scenario builder
            max_checks: Maximum number of endpoints to check

        Returns:
            Dictionary with check results
        """
        if not endpoints:
            return {"checked": 0, "accessible": 0, "errors": []}

        # Select sample endpoints (prefer GET requests)
        sample_endpoints = []
        get_endpoints = [ep for ep in endpoints if ep["method"] == "GET"]
        other_endpoints = [ep for ep in endpoints if ep["method"] != "GET"]

        # Prioritize GET endpoints for health checks
        sample_endpoints.extend(get_endpoints[:max_checks])
        if len(sample_endpoints) < max_checks:
            sample_endpoints.extend(other_endpoints[:max_checks - len(sample_endpoints)])

        results = {
            "checked": 0,
            "accessible": 0,
            "errors": []
        }

        print(f"🔍 Checking sample endpoints ({min(len(sample_endpoints), max_checks)} of {len(endpoints)})...")

        for i, endpoint in enumerate(sample_endpoints[:max_checks]):
            if i >= max_checks:
                break

            try:
                # Build URL with sample path parameters
                path = endpoint["path"]
                for param_name, param_value in endpoint.get("path_params", {}).items():
                    path = path.replace(f"{{{param_name}}}", str(param_value))

                url = urljoin(self.base_url + "/", path.lstrip("/"))
                method = endpoint["method"]

                # Make request (HEAD for non-GET to avoid side effects)
                request_method = "HEAD" if method != "GET" else "GET"
                response = requests.request(
                    request_method,
                    url,
                    headers=self.auth_headers,
                    timeout=5,
                    params=endpoint.get("query_params", {}) if method == "GET" else None
                )

                results["checked"] += 1

                if response.status_code < 500:  # Accept 4xx as "accessible"
                    results["accessible"] += 1
                    status_icon = "✅" if response.status_code < 400 else "⚠️ "
                    print(f"   {status_icon} {method} {path} → HTTP {response.status_code}")
                else:
                    error = f"HTTP {response.status_code}"
                    results["errors"].append(f"{method} {path}: {error}")
                    print(f"   💀 {method} {path} → {error}")

            except requests.exceptions.Timeout:
                results["checked"] += 1
                error = "Timeout"
                results["errors"].append(f"{endpoint['method']} {endpoint['path']}: {error}")
                print(f"   💀 {endpoint['method']} {endpoint['path']} → {error}")

            except Exception as e:
                results["checked"] += 1
                error = str(e)[:50]
                results["errors"].append(f"{endpoint['method']} {endpoint['path']}: {error}")
                print(f"   💀 {endpoint['method']} {endpoint['path']} → {error}")

        # Summary
        if results["checked"] > 0:
            success_rate = (results["accessible"] / results["checked"]) * 100
            print(f"📊 Endpoint check: {results['accessible']}/{results['checked']} accessible ({success_rate:.1f}%)")

        return results


def setup_logging():
    """Setup logging configuration for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def save_json_report(data: Dict[str, Any], filename: str):
    """Save data as JSON report in reports directory."""
    reports_dir = os.getenv("REPORTS_DIR", "/mnt/locust/reports")
    os.makedirs(reports_dir, exist_ok=True)

    filepath = os.path.join(reports_dir, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"📄 Report saved: {filepath}")


if __name__ == "__main__":
    # Test utilities
    print("🧪 Testing utilities...")

    # Test environment validation
    errors = EnvironmentValidator.validate_configuration()
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ Configuration validation passed")

    # Print configuration summary
    EnvironmentValidator.print_configuration_summary()