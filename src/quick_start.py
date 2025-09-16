#!/usr/bin/env python3
"""
Quick Start Script - Dynamic Stress Testing Framework

This script provides an interactive setup and demo for developers who want
to get started with the framework quickly. Perfect for first-time users!
"""

import os
import sys
import time
import subprocess
import shutil
from pathlib import Path

class QuickStart:
    """Interactive quick start guide."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.examples_dir = self.project_root / "examples"
        self.scenarios_dir = self.project_root / "scenarios"

    def run(self):
        """Run the interactive quick start."""
        self._print_banner()
        self._check_prerequisites()

        while True:
            choice = self._show_menu()

            if choice == "1":
                self._quick_demo_petstore()
            elif choice == "2":
                self._setup_your_api()
            elif choice == "3":
                self._run_local_mock_server()
            elif choice == "4":
                self._show_troubleshooting()
            elif choice == "5":
                self._show_advanced_scenarios()
            elif choice == "6":
                self._show_resources()
            elif choice == "7":
                print("👋 Happy load testing!")
                break
            else:
                print("💀 Invalid choice. Please try again.")

            input("\nPress Enter to continue...")

    def _print_banner(self):
        """Print welcome banner."""
        print(" DYNAMIC STRESS TESTING FRAMEWORK")
        print("=" * 50)
        print("Welcome! This tool helps you:")
        print("  ✅ Test APIs automatically from OpenAPI specs")
        print("  ✅ Handle authentication (JWT, login, API keys)")
        print("  ✅ Generate visual reports and analytics")
        print("  ✅ Run various load testing scenarios")
        print("=" * 50)

    def _check_prerequisites(self):
        """Check if prerequisites are installed."""
        print("\n🔍 Checking prerequisites...")

        # Check Docker
        try:
            subprocess.run(['docker', '--version'], capture_output=True, check=True)
            print("  ✅ Docker is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  💀 Docker is not installed")
            print("     Please install Docker Desktop: https://docker.com/get-started")
            return False

        # Check Docker Compose
        compose_working = False
        for cmd in ['docker compose', 'docker-compose']:
            try:
                subprocess.run(cmd.split() + ['--version'], capture_output=True, check=True)
                print(f"  ✅ {cmd} is working")
                compose_working = True
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        if not compose_working:
            print("  💀 Docker Compose is not working")
            return False

        # Check Python
        if sys.version_info >= (3, 7):
            print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        else:
            print(f"  💀 Python {sys.version_info.major}.{sys.version_info.minor} (need 3.7+)")
            return False

        return True

    def _show_menu(self):
        """Show main menu and get user choice."""
        print("\n" + "=" * 50)
        print("📋 QUICK START MENU")
        print("=" * 50)
        print("1. 🎯 Quick Demo (Swagger Petstore)")
        print("2. ⚙️  Setup Your API")
        print("3. 🖥️  Run Local Mock Server")
        print("4. 🔧 Troubleshooting")
        print("5. 🎭 Advanced Scenarios")
        print("6. 📚 Resources & Help")
        print("7. 🚪 Exit")

        return input("\nChoose an option (1-7): ").strip()

    def _quick_demo_petstore(self):
        """Quick demo with Swagger Petstore."""
        print("\n🎯 QUICK DEMO WITH SWAGGER PETSTORE")
        print("-" * 40)
        print("This demo uses the public Swagger Petstore API.")
        print("Perfect for learning the framework!")

        # Copy example config
        print("\n1. Setting up configuration...")
        try:
            shutil.copy2(self.examples_dir / ".env.petstore", ".env")
            print("   ✅ Copied petstore configuration to .env")
        except Exception as e:
            print(f"   💀 Failed to copy config: {e}")
            return

        # Quick endpoint analysis
        print("\n2. Analyzing API endpoints...")
        try:
            env = os.environ.copy()
            env.update({
                "OPENAPI_URL": "https://petstore3.swagger.io/api/v3/openapi.json",
                "BASE_URL": "https://petstore3.swagger.io/api/v3"
            })

            result = subprocess.run([
                sys.executable, "endpoint_visualizer.py", "--no-health-check"
            ], env=env, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print("   ✅ API analysis completed!")
                print("     Check reports/endpoint_analysis.json for details")
            else:
                print(f"   ⚠️  Analysis had issues: {result.stderr[:100]}...")

        except Exception as e:
            print(f"   ⚠️  Analysis failed: {e}")

        # Offer to run load test
        print("\n3. Ready to run load test!")
        print("   This will:")
        print("   - Test 19 API endpoints automatically")
        print("   - Generate real-time statistics")
        print("   - Create detailed HTML reports")

        choice = input("\n Start load test now? (y/N): ").lower()
        if choice == 'y':
            self._run_load_test()
        else:
            print("\n💡 To run manually:")
            print("   docker compose up --build")
            print("   Open http://localhost:8089")

    def _setup_your_api(self):
        """Help user setup their own API."""
        print("\n⚙️  SETUP YOUR API")
        print("-" * 25)

        # Get API details
        print("Let's configure your API for load testing:")

        openapi_url = input("\n📋 OpenAPI spec URL (e.g., https://api.example.com/openapi.json): ").strip()
        if not openapi_url:
            print("💀 OpenAPI URL is required")
            return

        base_url = input("🌐 API base URL (e.g., https://api.example.com): ").strip()
        if not base_url:
            print("💀 Base URL is required")
            return

        # Authentication
        print("\n🔐 Authentication (choose one):")
        print("1. None (public API)")
        print("2. JWT Token")
        print("3. API Key")
        print("4. Username/Password Login")

        auth_choice = input("Authentication type (1-4): ").strip()

        # Build configuration
        config_lines = [
            f"OPENAPI_URL={openapi_url}",
            f"BASE_URL={base_url}",
            "",
            "# Load testing settings",
            "MAX_USERS=25",
            "SPAWN_RATE=3",
            "REQUEST_TIMEOUT=15",
            "RETRY_COUNT=2",
            "",
            "# Reports",
            "REPORTS_DIR=/mnt/locust/reports",
            ""
        ]

        if auth_choice == "1":
            config_lines.extend([
                "# No authentication",
                "AUTH_MODE=none"
            ])
        elif auth_choice == "2":
            jwt_token = input("JWT token: ").strip()
            config_lines.extend([
                "# JWT Authentication",
                "AUTH_MODE=jwt",
                f"JWT_TOKEN={jwt_token}"
            ])
        elif auth_choice == "3":
            api_key = input("API key: ").strip()
            header_name = input("Header name (default: X-API-Key): ").strip() or "X-API-Key"
            config_lines.extend([
                "# API Key Authentication",
                "AUTH_MODE=apikey",
                f"API_KEY={api_key}",
                f"API_KEY_HEADER={header_name}"
            ])
        elif auth_choice == "4":
            login_url = input("Login endpoint (e.g., /auth/login): ").strip()
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            config_lines.extend([
                "# Login Authentication",
                "AUTH_MODE=login",
                f"LOGIN_URL={login_url}",
                f"LOGIN_USER={username}",
                f"LOGIN_PASS={password}"
            ])

        # Safety settings
        print("\n⚠️  For safety, we'll start with conservative settings:")
        print("   - Max 25 users")
        print("   - Only read operations by default")

        exclude_dangerous = input("Exclude write operations (POST/PUT/DELETE)? (Y/n): ").lower()
        if exclude_dangerous != 'n':
            config_lines.extend([
                "",
                "# Safety: exclude write operations",
                "SPEC_EXCLUDE_TAGS=write,post,put,delete,admin"
            ])

        # Save configuration
        try:
            with open(".env", "w") as f:
                f.write("\n".join(config_lines))
            print("\n✅ Configuration saved to .env")

            # Test configuration
            print("\n🧪 Testing configuration...")
            result = subprocess.run([
                sys.executable, "scenarios/troubleshoot.py", "--quick"
            ], capture_output=True, text=True)

            if "System ready" in result.stdout:
                print("✅ Configuration looks good!")

                choice = input("\n Run endpoint analysis? (Y/n): ").lower()
                if choice != 'n':
                    subprocess.run([sys.executable, "endpoint_visualizer.py", "--no-health-check"])

            else:
                print("⚠️  Configuration issues detected")
                print("Run: python3 scenarios/troubleshoot.py")

        except Exception as e:
            print(f"💀 Failed to save configuration: {e}")

    def _run_local_mock_server(self):
        """Setup and run local mock server."""
        print("\n🖥️  LOCAL MOCK SERVER")
        print("-" * 25)
        print("This starts a realistic mock API for testing the framework")
        print("Perfect for development and CI/CD!")

        # Check if Flask is available
        try:
            import flask
            print("✅ Flask is available")
        except ImportError:
            print("💀 Flask not installed")
            choice = input("Install Flask now? (Y/n): ").lower()
            if choice != 'n':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "flask"], check=True)
                    print("✅ Flask installed")
                except subprocess.CalledProcessError:
                    print("💀 Failed to install Flask")
                    return

        print("\n📋 Mock server provides:")
        print("   - RESTful API (users, posts)")
        print("   - Authentication testing")
        print("   - Realistic response times")
        print("   - Error simulation (5% rate)")

        choice = input("\n Start mock server? (Y/n): ").lower()
        if choice == 'n':
            return

        # Copy mock server config
        try:
            shutil.copy2(self.examples_dir / ".env.mock_server", ".env")
            print("✅ Mock server configuration copied")
        except Exception as e:
            print(f"💀 Failed to copy config: {e}")
            return

        print("\n🖥️  Starting mock server...")
        print("   URL: http://localhost:5000")
        print("   OpenAPI: http://localhost:5000/openapi.json")
        print("   Health: http://localhost:5000/health")
        print("\n💡 In another terminal, run:")
        print("   docker compose up --build")
        print("   Open http://localhost:8089")
        print("\n🛑 Press Ctrl+C to stop the server")

        try:
            subprocess.run([sys.executable, "tests/mock_api_server.py"])
        except KeyboardInterrupt:
            print("\n🛑 Mock server stopped")

    def _show_troubleshooting(self):
        """Show troubleshooting options."""
        print("\n🔧 TROUBLESHOOTING")
        print("-" * 20)

        print("Choose troubleshooting option:")
        print("1. Quick health check")
        print("2. Full diagnostics")
        print("3. Common problems & fixes")

        choice = input("Option (1-3): ").strip()

        if choice == "1":
            subprocess.run([sys.executable, "scenarios/troubleshoot.py", "--quick"])
        elif choice == "2":
            subprocess.run([sys.executable, "scenarios/troubleshoot.py"])
        elif choice == "3":
            self._show_common_problems()

    def _show_common_problems(self):
        """Show common problems and solutions."""
        print("\n🔧 COMMON PROBLEMS & FIXES")
        print("-" * 35)

        problems = [
            {
                "problem": "Docker not working",
                "symptoms": "Command not found, connection refused",
                "solutions": [
                    "Install Docker Desktop",
                    "Start Docker service: sudo systemctl start docker",
                    "Check Docker daemon is running"
                ]
            },
            {
                "problem": "OpenAPI spec not loading",
                "symptoms": "Connection timeout, invalid JSON",
                "solutions": [
                    "Check URL is accessible in browser",
                    "Verify it returns valid JSON/YAML",
                    "Try: curl -v YOUR_OPENAPI_URL"
                ]
            },
            {
                "problem": "Authentication failing",
                "symptoms": "401 errors, missing token",
                "solutions": [
                    "Verify token is valid and not expired",
                    "Check token format (JWT_TOKEN=your.jwt.token)",
                    "Test auth manually: curl -H 'Authorization: Bearer TOKEN' API_URL"
                ]
            },
            {
                "problem": "No endpoints found",
                "symptoms": "0 scenarios generated",
                "solutions": [
                    "Check SPEC_INCLUDE_TAGS / SPEC_EXCLUDE_TAGS",
                    "Verify OpenAPI spec has 'paths' section",
                    "Try without tag filters first"
                ]
            },
            {
                "problem": "Locust UI not accessible",
                "symptoms": "http://localhost:8089 not loading",
                "solutions": [
                    "Check Docker container is running: docker ps",
                    "Verify port mapping: docker compose logs",
                    "Try: docker compose down && docker compose up --build"
                ]
            }
        ]

        for i, problem in enumerate(problems, 1):
            print(f"\n{i}. {problem['problem'].upper()}")
            print(f"   Symptoms: {problem['symptoms']}")
            print("   Solutions:")
            for solution in problem['solutions']:
                print(f"     • {solution}")

    def _show_advanced_scenarios(self):
        """Show advanced testing scenarios."""
        print("\n🎭 ADVANCED SCENARIOS")
        print("-" * 25)

        scenarios = [
            ("Spike Test", "scenarios/spike_test.sh", "Sudden traffic surge"),
            ("Soak Test", "scenarios/soak_test.sh", "Long-duration endurance"),
            ("Interactive Demo", "examples/quick_demo.py", "Explore different APIs"),
            ("Custom Configuration", "examples/", "Ready-made .env files")
        ]

        for i, (name, path, description) in enumerate(scenarios, 1):
            print(f"{i}. {name}")
            print(f"   {description}")
            print(f"   Run: {path}")

        print("\n💡 You can also:")
        print("   • Customize .env for your specific needs")
        print("   • Use tag filtering to test specific endpoints")
        print("   • Adjust MAX_USERS and SPAWN_RATE for your API")
        print("   • Generate HTML reports with endpoint_visualizer.py")

    def _show_resources(self):
        """Show helpful resources."""
        print("\n📚 RESOURCES & HELP")
        print("-" * 22)

        resources = [
            ("Framework Documentation", "README.md"),
            ("Example Configurations", "examples/ directory"),
            ("Testing Scenarios", "scenarios/ directory"),
            ("Troubleshooting Tool", "scenarios/troubleshoot.py"),
            ("Endpoint Analyzer", "endpoint_visualizer.py"),
            ("Mock API Server", "tests/mock_api_server.py"),
            ("Comprehensive Tests", "test_framework.py")
        ]

        for name, location in resources:
            print(f"📄 {name}")
            print(f"   Location: {location}")

        print("\n🌐 External Resources:")
        print("   • Locust Documentation: https://docs.locust.io/")
        print("   • OpenAPI Specification: https://swagger.io/specification/")
        print("   • Docker Documentation: https://docs.docker.com/")

        print("\n💡 Quick Commands:")
        print("   # Analyze any API")
        print("   OPENAPI_URL=your-url python3 endpoint_visualizer.py")
        print()
        print("   # Quick health check")
        print("   python3 scenarios/troubleshoot.py --quick")
        print()
        print("   # Interactive demo")
        print("   python3 examples/quick_demo.py")

    def _run_load_test(self):
        """Run a load test."""
        print("\n STARTING LOAD TEST")
        print("-" * 25)
        print("This will run for 2 minutes with 10 concurrent users")

        try:
            # Start load test
            env = os.environ.copy()
            env.update({
                "MAX_USERS": "10",
                "SPAWN_RATE": "2",
                "RUN_TIME": "2m"
            })

            print("⚡ Running load test...")
            result = subprocess.run([
                "docker", "compose", "run", "--rm", "locust"
            ], env=env)

            if result.returncode == 0:
                print("✅ Load test completed!")
                print("📊 Check reports/ directory for detailed results")
            else:
                print("⚠️  Load test had issues")

        except KeyboardInterrupt:
            print("\n🛑 Load test interrupted")
        except Exception as e:
            print(f"💀 Load test failed: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Quick Start Script for Dynamic Stress Testing Framework")
        print()
        print("Usage:")
        print("  python3 quick_start.py        # Interactive mode")
        print("  python3 quick_start.py --help # Show this help")
        return

    quick_start = QuickStart()
    quick_start.run()


if __name__ == "__main__":
    main()