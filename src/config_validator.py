"""
Configuration validation and health checks for the Dynamic Stress Tests framework.
"""

import os
import re
import requests
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

from logger import get_logger, log_safety_check
from exceptions import ConfigurationError, ValidationError, NetworkError


class ConfigValidator:
    """Validates configuration and performs health checks."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate entire configuration.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()

        # Core validation
        self._validate_openapi_config()
        self._validate_base_url()
        self._validate_auth_config()
        self._validate_load_test_config()
        self._validate_safety_limits()
        self._validate_environment()

        is_valid = len(self.errors) == 0
        log_safety_check(self.logger, "Configuration validation", is_valid)

        return is_valid, self.errors.copy(), self.warnings.copy()

    def _validate_openapi_config(self):
        """Validate OpenAPI configuration."""
        openapi_url = os.getenv("OPENAPI_URL")
        openapi_path = os.getenv("OPENAPI_PATH")

        if not openapi_url and not openapi_path:
            self.errors.append("Either OPENAPI_URL or OPENAPI_PATH must be provided")
            return

        if openapi_url and openapi_path:
            self.warnings.append("Both OPENAPI_URL and OPENAPI_PATH provided, OPENAPI_PATH will be ignored")

        # Validate URL format
        if openapi_url:
            if not self._is_valid_url(openapi_url):
                self.errors.append(f"Invalid OPENAPI_URL format: {openapi_url}")
            elif not openapi_url.lower().endswith(('.json', '.yaml', '.yml')):
                self.warnings.append("OPENAPI_URL should typically end with .json, .yaml, or .yml")

        # Validate local path
        if openapi_path and not openapi_url:
            if not os.path.exists(openapi_path):
                self.errors.append(f"OPENAPI_PATH file not found: {openapi_path}")
            elif not openapi_path.lower().endswith(('.json', '.yaml', '.yml')):
                self.errors.append(f"OPENAPI_PATH must be a .json, .yaml, or .yml file: {openapi_path}")

    def _validate_base_url(self):
        """Validate base URL configuration."""
        base_url = os.getenv("BASE_URL")

        if not base_url:
            self.errors.append("BASE_URL is required")
            return

        if not self._is_valid_url(base_url):
            self.errors.append(f"Invalid BASE_URL format: {base_url}")
            return

        # Check for common issues
        if base_url.endswith('/'):
            self.warnings.append("BASE_URL should not end with '/', it will be handled automatically")

        if 'localhost' in base_url.lower() or '127.0.0.1' in base_url:
            self.warnings.append("BASE_URL points to localhost - ensure this is intended for your test environment")

    def _validate_auth_config(self):
        """Validate authentication configuration."""
        auth_mode = os.getenv("AUTH_MODE", "").lower()

        if not auth_mode or auth_mode == "none":
            self.warnings.append("No authentication configured - ensure your API doesn't require auth")
            return

        valid_modes = ["jwt", "login", "apikey", "oauth", "basic"]
        if auth_mode not in valid_modes:
            self.errors.append(f"Invalid AUTH_MODE: {auth_mode}. Valid options: {', '.join(valid_modes)}")
            return

        # Mode-specific validation
        if auth_mode == "jwt":
            jwt_token = os.getenv("JWT_TOKEN")
            if not jwt_token:
                self.errors.append("JWT_TOKEN is required when AUTH_MODE=jwt")
            elif len(jwt_token.split('.')) != 3:
                self.warnings.append("JWT_TOKEN format appears invalid (should have 3 parts separated by dots)")

        elif auth_mode == "login":
            required_vars = ["LOGIN_URL", "LOGIN_USER", "LOGIN_PASS"]
            for var in required_vars:
                if not os.getenv(var):
                    self.errors.append(f"{var} is required when AUTH_MODE=login")

            login_url = os.getenv("LOGIN_URL")
            if login_url and not login_url.startswith(('http', '/')):
                self.warnings.append("LOGIN_URL should be absolute URL or start with '/'")

        elif auth_mode == "apikey":
            if not os.getenv("API_KEY"):
                self.errors.append("API_KEY is required when AUTH_MODE=apikey")
            api_key_header = os.getenv("API_KEY_HEADER", "X-API-Key")
            if not re.match(r'^[A-Za-z][A-Za-z0-9-_]*$', api_key_header):
                self.warnings.append(f"API_KEY_HEADER '{api_key_header}' may not be a valid HTTP header name")

        elif auth_mode == "oauth":
            required_vars = ["OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET", "OAUTH_TOKEN_URL"]
            for var in required_vars:
                if not os.getenv(var):
                    self.errors.append(f"{var} is required when AUTH_MODE=oauth")

        elif auth_mode == "basic":
            required_vars = ["BASIC_USER", "BASIC_PASS"]
            for var in required_vars:
                if not os.getenv(var):
                    self.errors.append(f"{var} is required when AUTH_MODE=basic")

    def _validate_load_test_config(self):
        """Validate load testing configuration."""
        # Max users validation
        max_users = os.getenv("MAX_USERS", "100")
        try:
            max_users_int = int(max_users)
            if max_users_int <= 0:
                self.errors.append("MAX_USERS must be a positive integer")
            elif max_users_int > 10000:
                self.warnings.append(f"MAX_USERS is very high ({max_users_int}) - ensure this is intended")
        except ValueError:
            self.errors.append(f"MAX_USERS must be an integer, got: {max_users}")

        # Spawn rate validation
        spawn_rate = os.getenv("SPAWN_RATE", "5")
        try:
            spawn_rate_float = float(spawn_rate)
            if spawn_rate_float <= 0:
                self.errors.append("SPAWN_RATE must be a positive number")
            elif spawn_rate_float > 1000:
                self.warnings.append(f"SPAWN_RATE is very high ({spawn_rate_float}) - may cause system stress")
        except ValueError:
            self.errors.append(f"SPAWN_RATE must be a number, got: {spawn_rate}")

        # Timeout validation
        request_timeout = os.getenv("REQUEST_TIMEOUT", "10")
        try:
            timeout_int = int(request_timeout)
            if timeout_int <= 0:
                self.errors.append("REQUEST_TIMEOUT must be a positive integer")
            elif timeout_int > 300:
                self.warnings.append(f"REQUEST_TIMEOUT is very high ({timeout_int}s) - may cause slow tests")
        except ValueError:
            self.errors.append(f"REQUEST_TIMEOUT must be an integer, got: {request_timeout}")

        # Retry count validation
        retry_count = os.getenv("RETRY_COUNT", "1")
        try:
            retry_int = int(retry_count)
            if retry_int < 0:
                self.errors.append("RETRY_COUNT must be zero or positive")
            elif retry_int > 10:
                self.warnings.append(f"RETRY_COUNT is high ({retry_int}) - may mask real issues")
        except ValueError:
            self.errors.append(f"RETRY_COUNT must be an integer, got: {retry_count}")

        # Run time validation
        run_time = os.getenv("RUN_TIME")
        if run_time:
            if not re.match(r'^\d+[smh]?$', run_time):
                self.errors.append("RUN_TIME format should be like '10m', '30s', '1h', or '300'")

    def _validate_safety_limits(self):
        """Validate safety limits to prevent accidental damage."""
        base_url = os.getenv("BASE_URL", "")

        # Production domain detection
        production_indicators = [
            'prod', 'production', 'live', 'www.',
            '.com', '.org', '.net', '.gov'
        ]

        if any(indicator in base_url.lower() for indicator in production_indicators):
            max_users = int(os.getenv("MAX_USERS", "100"))
            if max_users > 100:
                self.warnings.append(
                    f"HIGH RISK: Testing against production-like URL ({base_url}) "
                    f"with {max_users} users. Consider using staging environment."
                )

        # Destructive operations check
        exclude_tags = os.getenv("SPEC_EXCLUDE_TAGS", "").lower()
        if "delete" not in exclude_tags and "admin" not in exclude_tags:
            self.warnings.append(
                "Consider excluding destructive operations: SPEC_EXCLUDE_TAGS=delete,admin"
            )

    def _validate_environment(self):
        """Validate environment setup."""
        # Check required directories
        reports_dir = os.getenv("REPORTS_DIR", "/app/reports")
        if not os.path.exists(os.path.dirname(reports_dir)) and reports_dir != "/app/reports":
            self.warnings.append(f"REPORTS_DIR parent directory doesn't exist: {reports_dir}")

        # Check extra headers format
        extra_headers = os.getenv("EXTRA_HEADERS")
        if extra_headers:
            try:
                import json
                json.loads(extra_headers)
            except json.JSONDecodeError:
                self.errors.append("EXTRA_HEADERS must be valid JSON")

        # Check for common Docker issues
        if os.path.exists("/.dockerenv"):
            # Running in Docker
            if not os.path.exists("/mnt/locust"):
                self.warnings.append("Running in Docker but /mnt/locust doesn't exist")

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL format is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Dictionary with health check results
        """
        self.logger.info("Starting health check...")

        results = {
            "overall_status": "unknown",
            "timestamp": None,
            "checks": {}
        }

        import datetime
        results["timestamp"] = datetime.datetime.now().isoformat()

        # Configuration validation
        is_valid, errors, warnings = self.validate_all()
        results["checks"]["configuration"] = {
            "status": "pass" if is_valid else "fail",
            "errors": errors,
            "warnings": warnings
        }

        # Network connectivity
        results["checks"]["network"] = self._check_network_connectivity()

        # OpenAPI accessibility
        results["checks"]["openapi"] = self._check_openapi_access()

        # Authentication
        results["checks"]["authentication"] = self._check_authentication()

        # System resources
        results["checks"]["system"] = self._check_system_resources()

        # Determine overall status
        check_statuses = [check["status"] for check in results["checks"].values()]
        if all(status == "pass" for status in check_statuses):
            results["overall_status"] = "healthy"
        elif any(status == "fail" for status in check_statuses):
            results["overall_status"] = "unhealthy"
        else:
            results["overall_status"] = "degraded"

        self.logger.info(f"Health check completed: {results['overall_status']}")
        return results

    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity to target."""
        base_url = os.getenv("BASE_URL")
        if not base_url:
            return {"status": "skip", "reason": "No BASE_URL configured"}

        try:
            response = requests.get(base_url, timeout=10)
            return {
                "status": "pass",
                "response_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except requests.exceptions.Timeout:
            return {"status": "fail", "error": "Connection timeout"}
        except requests.exceptions.ConnectionError:
            return {"status": "fail", "error": "Connection refused"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}

    def _check_openapi_access(self) -> Dict[str, Any]:
        """Check OpenAPI specification accessibility."""
        openapi_url = os.getenv("OPENAPI_URL")
        openapi_path = os.getenv("OPENAPI_PATH")

        if openapi_path:
            if os.path.exists(openapi_path):
                return {"status": "pass", "source": "local_file"}
            else:
                return {"status": "fail", "error": f"File not found: {openapi_path}"}

        if openapi_url:
            try:
                response = requests.get(openapi_url, timeout=10)
                response.raise_for_status()
                return {
                    "status": "pass",
                    "source": "remote_url",
                    "response_code": response.status_code,
                    "size_bytes": len(response.content)
                }
            except Exception as e:
                return {"status": "fail", "error": str(e)}

        return {"status": "skip", "reason": "No OpenAPI source configured"}

    def _check_authentication(self) -> Dict[str, Any]:
        """Check authentication configuration."""
        auth_mode = os.getenv("AUTH_MODE", "").lower()

        if not auth_mode or auth_mode == "none":
            return {"status": "skip", "reason": "No authentication configured"}

        try:
            # Import here to avoid circular imports
            from auth import AuthenticationManager
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()

            return {
                "status": "pass",
                "method": auth_mode,
                "headers_count": len(headers)
            }
        except Exception as e:
            return {
                "status": "fail",
                "method": auth_mode,
                "error": str(e)
            }

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources."""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            status = "pass"
            warnings = []

            if cpu_percent > 80:
                warnings.append(f"High CPU usage: {cpu_percent}%")
                status = "warn"

            if memory.percent > 80:
                warnings.append(f"High memory usage: {memory.percent}%")
                status = "warn"

            if disk.percent > 90:
                warnings.append(f"High disk usage: {disk.percent}%")
                status = "warn"

            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "warnings": warnings
            }
        except ImportError:
            return {"status": "skip", "reason": "psutil not available"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}


# Convenience functions
def validate_config() -> Tuple[bool, List[str], List[str]]:
    """Quick configuration validation."""
    validator = ConfigValidator()
    return validator.validate_all()


def run_health_check() -> Dict[str, Any]:
    """Quick health check."""
    validator = ConfigValidator()
    return validator.health_check()


# CLI-friendly validation
def validate_and_exit():
    """Validate configuration and exit with appropriate code."""
    import sys

    validator = ConfigValidator()
    is_valid, errors, warnings = validator.validate_all()

    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
        print()

    if errors:
        print("💀 ERRORS:")
        for error in errors:
            print(f"   {error}")
        print("\nConfiguration validation failed!")
        sys.exit(1)
    else:
        print("✅ Configuration validation passed!")
        if warnings:
            print(f"   ({len(warnings)} warning(s) noted above)")
        sys.exit(0)


if __name__ == "__main__":
    validate_and_exit()