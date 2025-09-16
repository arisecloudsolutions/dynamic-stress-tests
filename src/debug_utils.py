"""
Development and debugging utilities for the Dynamic Stress Tests framework.
"""

import os
import sys
import json
import time
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests

from logger import get_logger
from config_validator import ConfigValidator
from auth import AuthenticationManager
from openapi_loader import load_openapi_spec
from scenario_builder import ScenarioBuilder


class DebugSession:
    """Interactive debugging session for the framework."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.start_time = datetime.now()
        self.session_id = f"debug_{int(time.time())}"

    def run_interactive_debug(self):
        """Run interactive debugging session."""
        print(f"🔧 Debug Session Started - {self.session_id}")
        print("=" * 50)

        while True:
            try:
                self._show_debug_menu()
                choice = input("\nSelect option (q to quit): ").strip().lower()

                if choice == 'q':
                    break
                elif choice == '1':
                    self._debug_configuration()
                elif choice == '2':
                    self._debug_authentication()
                elif choice == '3':
                    self._debug_openapi()
                elif choice == '4':
                    self._debug_scenarios()
                elif choice == '5':
                    self._debug_network()
                elif choice == '6':
                    self._show_environment()
                elif choice == '7':
                    self._test_single_endpoint()
                elif choice == '8':
                    self._export_debug_info()
                else:
                    print("Invalid option. Please try again.")

            except KeyboardInterrupt:
                print("\n\n👋 Debug session interrupted")
                break
            except Exception as e:
                print(f"\n💀 Error: {e}")
                traceback.print_exc()

        print(f"\n🏁 Debug session completed - {self.session_id}")

    def _show_debug_menu(self):
        """Show debug menu options."""
        print("\n🔧 Debug Options:")
        print("1. Check Configuration")
        print("2. Test Authentication")
        print("3. Analyze OpenAPI Spec")
        print("4. Test Scenario Generation")
        print("5. Network Connectivity")
        print("6. Show Environment")
        print("7. Test Single Endpoint")
        print("8. Export Debug Info")

    def _debug_configuration(self):
        """Debug configuration issues."""
        print("\n📋 Configuration Debug")
        print("-" * 25)

        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_all()

        if is_valid:
            print("✅ Configuration is valid!")
        else:
            print("💀 Configuration has errors:")
            for error in errors:
                print(f"   • {error}")

        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"   • {warning}")

        # Show current configuration
        print("\n📄 Current Configuration:")
        config_vars = [
            "OPENAPI_URL", "OPENAPI_PATH", "BASE_URL", "AUTH_MODE",
            "MAX_USERS", "SPAWN_RATE", "REQUEST_TIMEOUT"
        ]

        for var in config_vars:
            value = os.getenv(var, "Not set")
            # Mask sensitive values
            if "PASS" in var or "SECRET" in var or "TOKEN" in var:
                value = "***" if value != "Not set" else value
            print(f"   {var}: {value}")

    def _debug_authentication(self):
        """Debug authentication setup."""
        print("\n🔐 Authentication Debug")
        print("-" * 25)

        try:
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()

            print("✅ Authentication successful!")
            print(f"   Generated {len(headers)} headers")

            for key, value in headers.items():
                # Mask sensitive headers
                if any(sensitive in key.lower() for sensitive in ['authorization', 'key', 'token']):
                    masked_value = f"{value[:10]}***" if len(value) > 10 else "***"
                    print(f"   {key}: {masked_value}")
                else:
                    print(f"   {key}: {value}")

        except Exception as e:
            print(f"💀 Authentication failed: {e}")

    def _debug_openapi(self):
        """Debug OpenAPI specification loading."""
        print("\n📋 OpenAPI Debug")
        print("-" * 20)

        try:
            spec = load_openapi_spec()
            print("✅ OpenAPI spec loaded successfully!")

            # Basic info
            info = spec.get('info', {})
            print(f"   Title: {info.get('title', 'N/A')}")
            print(f"   Version: {info.get('version', 'N/A')}")

            # Paths analysis
            paths = spec.get('paths', {})
            print(f"   Paths: {len(paths)}")

            # Method breakdown
            methods = {}
            for path, operations in paths.items():
                for method in operations.keys():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        methods[method.upper()] = methods.get(method.upper(), 0) + 1

            print("   Methods:")
            for method, count in methods.items():
                print(f"     {method}: {count}")

            # Tags analysis
            all_tags = set()
            for path, operations in paths.items():
                for method, operation in operations.items():
                    tags = operation.get('tags', [])
                    all_tags.update(tags)

            if all_tags:
                print(f"   Tags: {', '.join(sorted(all_tags))}")

        except Exception as e:
            print(f"💀 OpenAPI loading failed: {e}")
            traceback.print_exc()

    def _debug_scenarios(self):
        """Debug scenario generation."""
        print("\n🎯 Scenario Debug")
        print("-" * 20)

        try:
            spec = load_openapi_spec()
            builder = ScenarioBuilder()

            include_tags = os.getenv("SPEC_INCLUDE_TAGS")
            exclude_tags = os.getenv("SPEC_EXCLUDE_TAGS")

            scenarios = builder.build_test_scenarios(spec, include_tags, exclude_tags)

            print(f"✅ Generated {len(scenarios)} test scenarios")

            if scenarios:
                print("\n📝 Sample scenarios:")
                for i, scenario in enumerate(scenarios[:5]):  # Show first 5
                    print(f"   {i+1}. {scenario['method']} {scenario['path']}")
                    if scenario.get('payload'):
                        print(f"      Payload: {json.dumps(scenario['payload'], indent=6)}")

                if len(scenarios) > 5:
                    print(f"   ... and {len(scenarios) - 5} more")

        except Exception as e:
            print(f"💀 Scenario generation failed: {e}")
            traceback.print_exc()

    def _debug_network(self):
        """Debug network connectivity."""
        print("\n🌐 Network Debug")
        print("-" * 18)

        base_url = os.getenv("BASE_URL")
        if not base_url:
            print("💀 BASE_URL not configured")
            return

        print(f"Testing connectivity to: {base_url}")

        try:
            start_time = time.time()
            response = requests.get(base_url, timeout=10)
            end_time = time.time()

            print(f"✅ Connection successful!")
            print(f"   Status: {response.status_code}")
            print(f"   Response time: {(end_time - start_time) * 1000:.0f}ms")
            print(f"   Headers: {len(response.headers)}")

            # Show some headers
            interesting_headers = ['content-type', 'server', 'x-powered-by']
            for header in interesting_headers:
                if header in response.headers:
                    print(f"   {header}: {response.headers[header]}")

        except requests.exceptions.Timeout:
            print("💀 Connection timed out")
        except requests.exceptions.ConnectionError:
            print("💀 Connection refused")
        except Exception as e:
            print(f"💀 Network error: {e}")

    def _show_environment(self):
        """Show environment information."""
        print("\n🌍 Environment Information")
        print("-" * 30)

        # Python info
        print(f"Python version: {sys.version}")
        print(f"Platform: {sys.platform}")

        # Docker info
        if os.path.exists("/.dockerenv"):
            print("Environment: Docker container")
        else:
            print("Environment: Local machine")

        # Working directory
        print(f"Working directory: {os.getcwd()}")

        # Environment variables
        print("\n🔧 Framework Environment Variables:")
        framework_vars = [var for var in os.environ.keys()
                         if any(keyword in var for keyword in
                               ['OPENAPI', 'BASE_URL', 'AUTH', 'MAX_', 'SPAWN_', 'REQUEST_'])]

        for var in sorted(framework_vars):
            value = os.environ[var]
            # Mask sensitive values
            if any(sensitive in var for sensitive in ['PASS', 'SECRET', 'TOKEN']):
                value = "***"
            print(f"   {var}: {value}")

    def _test_single_endpoint(self):
        """Test a single endpoint manually."""
        print("\n🎯 Single Endpoint Test")
        print("-" * 25)

        base_url = os.getenv("BASE_URL")
        if not base_url:
            print("💀 BASE_URL not configured")
            return

        path = input("Enter endpoint path (e.g., /users): ").strip()
        if not path:
            print("💀 No path provided")
            return

        method = input("HTTP method [GET]: ").strip().upper() or "GET"

        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

        try:
            # Get authentication headers
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()

            print(f"\nTesting: {method} {url}")
            print(f"Headers: {len(headers)} auth headers")

            start_time = time.time()
            response = requests.request(method, url, headers=headers, timeout=10)
            end_time = time.time()

            print(f"\n✅ Response received!")
            print(f"   Status: {response.status_code}")
            print(f"   Response time: {(end_time - start_time) * 1000:.0f}ms")
            print(f"   Content length: {len(response.content)} bytes")

            # Show response preview
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    preview = json.dumps(json_data, indent=2)
                    if len(preview) > 500:
                        preview = preview[:500] + "..."
                    print(f"\nResponse preview:\n{preview}")
                except:
                    print(f"\nResponse text preview:\n{response.text[:200]}...")
            else:
                print(f"\nResponse text preview:\n{response.text[:200]}...")

        except Exception as e:
            print(f"💀 Request failed: {e}")

    def _export_debug_info(self):
        """Export debug information to file."""
        print("\n💾 Export Debug Info")
        print("-" * 22)

        try:
            debug_info = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "environment": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "working_directory": os.getcwd(),
                    "is_docker": os.path.exists("/.dockerenv")
                },
                "configuration": {},
                "validation_results": {},
                "health_check": {}
            }

            # Collect configuration
            config_vars = [var for var in os.environ.keys()
                          if any(keyword in var for keyword in
                                ['OPENAPI', 'BASE_', 'AUTH', 'MAX_', 'SPAWN_', 'REQUEST_'])]

            for var in config_vars:
                value = os.environ[var]
                # Mask sensitive values
                if any(sensitive in var for sensitive in ['PASS', 'SECRET', 'TOKEN']):
                    value = "***MASKED***"
                debug_info["configuration"][var] = value

            # Run validation
            validator = ConfigValidator()
            is_valid, errors, warnings = validator.validate_all()
            debug_info["validation_results"] = {
                "is_valid": is_valid,
                "errors": errors,
                "warnings": warnings
            }

            # Run health check
            debug_info["health_check"] = validator.health_check()

            # Write to file
            reports_dir = os.getenv("REPORTS_DIR", "reports")
            os.makedirs(reports_dir, exist_ok=True)

            filename = f"{reports_dir}/debug_info_{self.session_id}.json"
            with open(filename, 'w') as f:
                json.dump(debug_info, f, indent=2)

            print(f"✅ Debug info exported to: {filename}")

        except Exception as e:
            print(f"💀 Export failed: {e}")


def quick_debug():
    """Run a quick debug check."""
    print("🔧 Quick Debug Check")
    print("=" * 20)

    # Configuration validation
    print("\n1. Configuration Check:")
    validator = ConfigValidator()
    is_valid, errors, warnings = validator.validate_all()

    if is_valid:
        print("   ✅ Configuration is valid")
    else:
        print("   💀 Configuration has errors:")
        for error in errors[:3]:  # Show first 3 errors
            print(f"      • {error}")
        if len(errors) > 3:
            print(f"      ... and {len(errors) - 3} more errors")

    # Authentication check
    print("\n2. Authentication Check:")
    try:
        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()
        print(f"   ✅ Authentication successful ({len(headers)} headers)")
    except Exception as e:
        print(f"   💀 Authentication failed: {e}")

    # Network check
    print("\n3. Network Check:")
    base_url = os.getenv("BASE_URL")
    if base_url:
        try:
            response = requests.get(base_url, timeout=5)
            print(f"   ✅ Network connectivity OK ({response.status_code})")
        except Exception as e:
            print(f"   💀 Network issue: {e}")
    else:
        print("   ⚠️  No BASE_URL configured")

    print("\n" + "=" * 20)
    print("Run 'python3 src/debug_utils.py' for interactive debugging")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Debug utilities for Dynamic Stress Tests")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run interactive debug session")
    parser.add_argument("--quick", "-q", action="store_true",
                       help="Run quick debug check")

    args = parser.parse_args()

    if args.interactive:
        debug_session = DebugSession()
        debug_session.run_interactive_debug()
    elif args.quick:
        quick_debug()
    else:
        # Default to interactive
        debug_session = DebugSession()
        debug_session.run_interactive_debug()