#!/usr/bin/env python3
"""
Troubleshooting Tool for Dynamic Stress Testing Framework

This script helps developers diagnose and fix common issues when setting up
or running load tests. It provides step-by-step guidance and automated fixes.
"""

import os
import sys
import json
import requests
import subprocess
from typing import List, Dict, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import EnvironmentValidator
from openapi_loader import OpenAPILoader
from auth import AuthenticationManager


class TroubleshootingTool:
    """Interactive troubleshooting tool for the framework."""

    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []

    def run_full_diagnostics(self):
        """Run comprehensive diagnostics."""
        print("🔧 DYNAMIC STRESS TESTING FRAMEWORK - TROUBLESHOOTING")
        print("=" * 60)
        print("This tool will help diagnose and fix common issues.")
        print("=" * 60)

        # Check 1: Environment Configuration
        print("\n1️⃣  Checking environment configuration...")
        self._check_environment_config()

        # Check 2: Docker Setup
        print("\n2️⃣  Checking Docker setup...")
        self._check_docker_setup()

        # Check 3: Network Connectivity
        print("\n3️⃣  Checking network connectivity...")
        self._check_network_connectivity()

        # Check 4: OpenAPI Specification
        print("\n4️⃣  Checking OpenAPI specification...")
        self._check_openapi_spec()

        # Check 5: Authentication
        print("\n5️⃣  Checking authentication...")
        self._check_authentication()

        # Check 6: Dependencies
        print("\n6️⃣  Checking Python dependencies...")
        self._check_dependencies()

        # Summary
        self._print_summary()

    def _check_environment_config(self):
        """Check environment configuration."""
        try:
            errors = EnvironmentValidator.validate_configuration()

            if not errors:
                print("   ✅ Environment configuration is valid")
            else:
                print(f"   ❌ Found {len(errors)} configuration issues:")
                for i, error in enumerate(errors, 1):
                    print(f"      {i}. {error}")
                    self.issues_found.append(f"Config: {error}")

                # Suggest fixes
                self._suggest_config_fixes(errors)

        except Exception as e:
            print(f"   ⚠️  Error checking configuration: {e}")
            self.issues_found.append(f"Config check failed: {e}")

    def _suggest_config_fixes(self, errors: List[str]):
        """Suggest fixes for configuration errors."""
        print("   💡 Suggested fixes:")

        for error in errors:
            if "OPENAPI_URL or OPENAPI_PATH" in error:
                print("      - Copy example config: cp examples/.env.petstore .env")
                print("      - Or set: export OPENAPI_URL=https://petstore3.swagger.io/api/v3/openapi.json")

            elif "BASE_URL" in error:
                print("      - Set: export BASE_URL=https://your-api.com")

            elif "JWT_TOKEN" in error:
                print("      - Set: export JWT_TOKEN=your-jwt-token")
                print("      - Or change to: export AUTH_MODE=none")

            elif "not a valid number" in error:
                print("      - Fix numeric values (e.g., MAX_USERS=50, SPAWN_RATE=5)")

    def _check_docker_setup(self):
        """Check Docker and Docker Compose setup."""
        try:
            # Check Docker
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Docker is installed")
            else:
                print("   ❌ Docker is not installed or not working")
                self.issues_found.append("Docker not available")

            # Check Docker Compose
            compose_commands = ['docker-compose', 'docker compose']
            compose_working = False

            for cmd in compose_commands:
                try:
                    result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"   ✅ {cmd} is working")
                        compose_working = True
                        break
                except FileNotFoundError:
                    continue

            if not compose_working:
                print("   ❌ Docker Compose is not working")
                self.issues_found.append("Docker Compose not available")
                print("   💡 Try: docker compose --version")

            # Check if Docker daemon is running
            result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
            if result.returncode != 0:
                print("   ❌ Docker daemon is not running")
                self.issues_found.append("Docker daemon not running")
                print("   💡 Start Docker Desktop or run: sudo systemctl start docker")

        except FileNotFoundError:
            print("   ❌ Docker is not installed")
            self.issues_found.append("Docker not installed")

    def _check_network_connectivity(self):
        """Check network connectivity to common endpoints."""
        test_urls = [
            ("Google DNS", "https://8.8.8.8", "Basic internet connectivity"),
            ("Swagger Petstore", "https://petstore3.swagger.io/api/v3/openapi.json", "Test API availability"),
            ("HTTPBin", "https://httpbin.org/get", "Testing service availability")
        ]

        for name, url, description in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {name}: {description}")
                else:
                    print(f"   ⚠️  {name}: HTTP {response.status_code}")
                    self.issues_found.append(f"Network: {name} returned {response.status_code}")

            except requests.exceptions.ConnectTimeout:
                print(f"   ❌ {name}: Connection timeout")
                self.issues_found.append(f"Network: {name} timeout")

            except requests.exceptions.ConnectionError:
                print(f"   ❌ {name}: Connection failed")
                self.issues_found.append(f"Network: {name} connection failed")

            except Exception as e:
                print(f"   ⚠️  {name}: {str(e)[:50]}...")

    def _check_openapi_spec(self):
        """Check OpenAPI specification loading."""
        openapi_url = os.getenv("OPENAPI_URL")
        openapi_path = os.getenv("OPENAPI_PATH")

        if not openapi_url and not openapi_path:
            print("   ⚠️  No OpenAPI source configured")
            return

        try:
            loader = OpenAPILoader()
            spec = loader.load_openapi()

            # Basic validation
            if spec and isinstance(spec, dict):
                paths_count = len(spec.get("paths", {}))
                api_title = spec.get("info", {}).get("title", "Unknown")
                print(f"   ✅ OpenAPI spec loaded: {api_title} ({paths_count} paths)")

                if paths_count == 0:
                    print("   ⚠️  No paths found in OpenAPI spec")
                    self.issues_found.append("OpenAPI spec has no paths")

            else:
                print("   ❌ OpenAPI spec is not valid")
                self.issues_found.append("Invalid OpenAPI spec format")

        except Exception as e:
            print(f"   ❌ Failed to load OpenAPI spec: {str(e)[:100]}...")
            self.issues_found.append(f"OpenAPI loading failed: {e}")

            # Suggest specific fixes
            if "not found" in str(e).lower():
                print("   💡 Check if the URL/path is correct")
            elif "timeout" in str(e).lower():
                print("   💡 Check network connectivity or try a different spec")
            elif "json" in str(e).lower():
                print("   💡 The endpoint might not return valid JSON/YAML")

    def _check_authentication(self):
        """Check authentication configuration."""
        auth_mode = os.getenv("AUTH_MODE", "").lower()

        if not auth_mode or auth_mode == "none":
            print("   ✅ No authentication configured (anonymous access)")
            return

        try:
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()

            if headers and any(key.lower() == "authorization" for key in headers.keys()):
                print(f"   ✅ Authentication configured ({auth_mode} mode)")
                print(f"      Headers: {len(headers)} configured")
            else:
                print(f"   ⚠️  Authentication configured but no Authorization header")
                self.issues_found.append("Auth configured but no auth header generated")

        except Exception as e:
            print(f"   ❌ Authentication failed: {str(e)[:100]}...")
            self.issues_found.append(f"Authentication error: {e}")

            # Suggest fixes based on auth mode
            if auth_mode == "jwt":
                print("   💡 Check JWT_TOKEN environment variable")
            elif auth_mode == "login":
                print("   💡 Check LOGIN_URL, LOGIN_USER, LOGIN_PASS variables")
            elif auth_mode == "apikey":
                print("   💡 Check API_KEY environment variable")

    def _check_dependencies(self):
        """Check Python dependencies."""
        required_packages = [
            ("locust", "Load testing framework"),
            ("requests", "HTTP client library"),
            ("flask", "For mock server (optional)")
        ]

        for package, description in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}: {description}")
            except ImportError:
                print(f"   ❌ {package}: Not installed - {description}")
                self.issues_found.append(f"Missing dependency: {package}")

        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 7):
            print(f"   ✅ Python {python_version.major}.{python_version.minor}: Compatible")
        else:
            print(f"   ❌ Python {python_version.major}.{python_version.minor}: Too old (need 3.7+)")
            self.issues_found.append("Python version too old")

    def _print_summary(self):
        """Print diagnostic summary."""
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)

        if not self.issues_found:
            print("🎉 No issues found! Your setup looks good.")
            print("\n🚀 Ready to run load tests:")
            print("   docker compose up --build")
            print("   Open http://localhost:8089")
        else:
            print(f"⚠️  Found {len(self.issues_found)} issues that need attention:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")

            print("\n💡 QUICK FIXES:")
            self._suggest_quick_fixes()

        print("=" * 60)

    def _suggest_quick_fixes(self):
        """Suggest quick fixes for common issues."""
        print("# For configuration issues:")
        print("cp examples/.env.petstore .env")
        print()
        print("# For dependency issues:")
        print("pip install -r requirements.txt")
        print()
        print("# For Docker issues:")
        print("# Make sure Docker Desktop is running")
        print("# Or: sudo systemctl start docker")
        print()
        print("# Test with mock server:")
        print("python3 tests/mock_api_server.py  # Terminal 1")
        print("cp examples/.env.mock_server .env && docker compose up  # Terminal 2")

    def run_quick_health_check(self):
        """Run a quick health check."""
        print("🏥 QUICK HEALTH CHECK")
        print("-" * 30)

        checks = [
            ("Configuration", self._quick_check_config),
            ("Docker", self._quick_check_docker),
            ("OpenAPI", self._quick_check_openapi),
            ("Authentication", self._quick_check_auth)
        ]

        results = {}
        for name, check_func in checks:
            try:
                results[name] = check_func()
                status = "✅" if results[name] else "❌"
                print(f"{status} {name}")
            except Exception as e:
                results[name] = False
                print(f"❌ {name}: {str(e)[:30]}...")

        # Summary
        passed = sum(results.values())
        total = len(results)
        print(f"\n📊 Health: {passed}/{total} checks passed")

        if passed == total:
            print("🎉 System ready for load testing!")
        else:
            print("⚠️  Run full diagnostics: python3 scenarios/troubleshoot.py")

    def _quick_check_config(self) -> bool:
        """Quick configuration check."""
        return len(EnvironmentValidator.validate_configuration()) == 0

    def _quick_check_docker(self) -> bool:
        """Quick Docker check."""
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True)
            return result.returncode == 0
        except:
            return False

    def _quick_check_openapi(self) -> bool:
        """Quick OpenAPI check."""
        try:
            loader = OpenAPILoader()
            spec = loader.load_openapi()
            return spec and len(spec.get("paths", {})) > 0
        except:
            return False

    def _quick_check_auth(self) -> bool:
        """Quick authentication check."""
        try:
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()
            return isinstance(headers, dict)
        except:
            return False


def main():
    """Main CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Troubleshooting tool for Dynamic Stress Testing Framework"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick health check only"
    )

    args = parser.parse_args()

    troubleshooter = TroubleshootingTool()

    if args.quick:
        troubleshooter.run_quick_health_check()
    else:
        troubleshooter.run_full_diagnostics()


if __name__ == "__main__":
    main()