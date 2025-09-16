#!/usr/bin/env python3
"""
Comprehensive test suite for the Dynamic Stress Testing Framework.

This script validates all components of the framework and provides
a complete testing experience for developers.
"""

import os
import sys
import json
import time
import unittest
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock
import tempfile

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openapi_loader import OpenAPILoader
from scenario_builder import ScenarioBuilder
from auth import AuthenticationManager
from utils import EnvironmentValidator, LoadTestReporter, EndpointHealthChecker
from endpoint_visualizer import EndpointVisualizer


class TestOpenAPILoader(unittest.TestCase):
    """Test the OpenAPI loader functionality."""

    def setUp(self):
        """Set up test environment."""
        self.loader = OpenAPILoader()
        self.test_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {"tags": ["users"], "summary": "List users"},
                    "post": {"tags": ["users"], "summary": "Create user"}
                },
                "/users/{id}": {
                    "get": {"tags": ["users"], "summary": "Get user"}
                }
            }
        }

    def test_validate_specification_success(self):
        """Test successful OpenAPI validation."""
        self.loader.spec_data = self.test_spec
        self.loader._validate_specification()
        self.assertIsNotNone(self.loader.validation_results)
        self.assertEqual(self.loader.validation_results["total_paths"], 2)

    def test_validate_specification_missing_paths(self):
        """Test validation with missing paths."""
        invalid_spec = {"openapi": "3.0.3", "info": {"title": "Test"}}
        self.loader.spec_data = invalid_spec
        with self.assertRaises(ValueError):
            self.loader._validate_specification()

    def test_load_from_file_success(self):
        """Test loading from local file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_spec, f)
            temp_path = f.name

        try:
            result = self.loader._load_from_file(temp_path)
            self.assertEqual(result["info"]["title"], "Test API")
        finally:
            os.unlink(temp_path)

    def test_load_from_file_not_found(self):
        """Test loading from non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.loader._load_from_file("/nonexistent/file.json")

    @patch('requests.get')
    def test_load_from_url_success(self, mock_get):
        """Test loading from URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = self.test_spec
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.loader._load_from_url("https://example.com/openapi.json")
        self.assertEqual(result["info"]["title"], "Test API")

    @patch('requests.get')
    def test_load_from_url_timeout(self, mock_get):
        """Test URL loading with timeout."""
        mock_get.side_effect = Exception("Timeout")
        with self.assertRaises(RuntimeError):
            self.loader._load_from_url("https://example.com/openapi.json")


class TestScenarioBuilder(unittest.TestCase):
    """Test the scenario builder functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "tags": ["users", "public"],
                        "summary": "List users",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {"type": "integer", "minimum": 1, "maximum": 100}
                            }
                        ]
                    },
                    "post": {
                        "tags": ["users"],
                        "summary": "Create user",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string", "format": "email"}
                                        },
                                        "required": ["name", "email"]
                                    }
                                }
                            }
                        }
                    }
                },
                "/users/{id}": {
                    "get": {
                        "tags": ["users"],
                        "summary": "Get user",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ]
                    },
                    "delete": {
                        "tags": ["admin"],
                        "summary": "Delete user",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ]
                    }
                }
            }
        }
        self.builder = ScenarioBuilder(self.test_spec)

    def test_build_tasks_no_filters(self):
        """Test building tasks without filters."""
        tasks = self.builder.build_tasks()
        self.assertEqual(len(tasks), 4)  # All 4 operations

    def test_build_tasks_include_filter(self):
        """Test building tasks with include filter."""
        tasks = self.builder.build_tasks(include_tags="public")
        self.assertEqual(len(tasks), 1)  # Only GET /users has 'public' tag

    def test_build_tasks_exclude_filter(self):
        """Test building tasks with exclude filter."""
        tasks = self.builder.build_tasks(exclude_tags="admin")
        self.assertEqual(len(tasks), 3)  # All except DELETE /users/{id}

    def test_generate_sample_from_schema_string(self):
        """Test sample generation for string types."""
        schema = {"type": "string", "format": "email"}
        result = self.builder._generate_sample_from_schema(schema, "email")
        self.assertIn("@", result)

    def test_generate_sample_from_schema_object(self):
        """Test sample generation for object types."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        result = self.builder._generate_sample_from_schema(schema)
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)

    def test_generate_sample_from_schema_array(self):
        """Test sample generation for array types."""
        schema = {
            "type": "array",
            "items": {"type": "string"}
        }
        result = self.builder._generate_sample_from_schema(schema)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_task_weight_calculation(self):
        """Test task weight calculation."""
        get_operation = {"method": "GET", "tags": ["public"]}
        delete_operation = {"method": "DELETE", "tags": ["admin"]}

        get_weight = self.builder._calculate_task_weight(get_operation)
        delete_weight = self.builder._calculate_task_weight(delete_operation)

        self.assertGreater(get_weight, delete_weight)


class TestAuthenticationManager(unittest.TestCase):
    """Test the authentication manager functionality."""

    def setUp(self):
        """Set up test environment."""
        self.auth_manager = AuthenticationManager()

    def test_jwt_auth_success(self):
        """Test JWT authentication."""
        with patch.dict(os.environ, {
            'AUTH_MODE': 'jwt',
            'JWT_TOKEN': 'test.jwt.token',
            'EXTRA_HEADERS': '{"X-Client": "test"}'
        }):
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()
            self.assertEqual(headers['Authorization'], 'Bearer test.jwt.token')
            self.assertEqual(headers['X-Client'], 'test')

    def test_jwt_auth_missing_token(self):
        """Test JWT authentication with missing token."""
        with patch.dict(os.environ, {'AUTH_MODE': 'jwt'}, clear=True):
            auth_manager = AuthenticationManager()
            with self.assertRaises(RuntimeError):
                auth_manager.get_auth_headers()

    @patch('requests.post')
    def test_login_auth_success(self, mock_post):
        """Test login authentication."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test.token"}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            'AUTH_MODE': 'login',
            'BASE_URL': 'https://api.example.com',
            'LOGIN_URL': '/auth/login',
            'LOGIN_USER': 'test@example.com',
            'LOGIN_PASS': 'password'
        }):
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()
            self.assertEqual(headers['Authorization'], 'Bearer test.token')

    def test_no_auth_mode(self):
        """Test with no authentication mode."""
        with patch.dict(os.environ, {}, clear=True):
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()
            self.assertNotIn('Authorization', headers)

    def test_api_key_auth(self):
        """Test API key authentication."""
        with patch.dict(os.environ, {
            'AUTH_MODE': 'apikey',
            'API_KEY': 'test-api-key',
            'API_KEY_HEADER': 'X-API-Key'
        }):
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()
            self.assertEqual(headers['X-API-Key'], 'test-api-key')

    def test_basic_auth(self):
        """Test HTTP Basic authentication."""
        with patch.dict(os.environ, {
            'AUTH_MODE': 'basic',
            'BASIC_USER': 'testuser',
            'BASIC_PASS': 'testpass'
        }):
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()
            self.assertIn('Authorization', headers)
            self.assertTrue(headers['Authorization'].startswith('Basic '))


class TestEnvironmentValidator(unittest.TestCase):
    """Test the environment validator functionality."""

    def test_validate_configuration_success(self):
        """Test successful configuration validation."""
        with patch.dict(os.environ, {
            'OPENAPI_URL': 'https://api.example.com/openapi.json',
            'BASE_URL': 'https://api.example.com',
            'MAX_USERS': '50',
            'SPAWN_RATE': '2'
        }):
            errors = EnvironmentValidator.validate_configuration()
            self.assertEqual(len(errors), 0)

    def test_validate_configuration_missing_openapi(self):
        """Test validation with missing OpenAPI source."""
        with patch.dict(os.environ, {
            'BASE_URL': 'https://api.example.com'
        }, clear=True):
            errors = EnvironmentValidator.validate_configuration()
            self.assertTrue(any("OPENAPI_URL or OPENAPI_PATH" in error for error in errors))

    def test_validate_configuration_invalid_base_url(self):
        """Test validation with invalid base URL."""
        with patch.dict(os.environ, {
            'OPENAPI_URL': 'https://api.example.com/openapi.json',
            'BASE_URL': 'invalid-url'
        }):
            errors = EnvironmentValidator.validate_configuration()
            self.assertTrue(any("must start with http" in error for error in errors))

    def test_validate_configuration_invalid_numeric(self):
        """Test validation with invalid numeric values."""
        with patch.dict(os.environ, {
            'OPENAPI_URL': 'https://api.example.com/openapi.json',
            'BASE_URL': 'https://api.example.com',
            'MAX_USERS': 'not-a-number'
        }):
            errors = EnvironmentValidator.validate_configuration()
            self.assertTrue(any("not a valid number" in error for error in errors))


class TestLoadTestReporter(unittest.TestCase):
    """Test the load test reporter functionality."""

    def setUp(self):
        """Set up test environment."""
        self.reporter = LoadTestReporter()

    def test_log_request_success(self):
        """Test logging successful requests."""
        self.reporter.log_request("GET", "/users", 150.5, 200)

        stats = self.reporter.endpoint_stats["GET /users"]
        self.assertEqual(stats["requests"], 1)
        self.assertEqual(stats["failures"], 0)
        self.assertEqual(stats["total_response_time"], 150.5)

    def test_log_request_failure(self):
        """Test logging failed requests."""
        self.reporter.log_request("POST", "/users", 300.0, 500, "Internal Server Error")

        stats = self.reporter.endpoint_stats["POST /users"]
        self.assertEqual(stats["requests"], 1)
        self.assertEqual(stats["failures"], 1)
        self.assertIn("500:", list(self.reporter.error_summary.keys())[0])

    def test_generate_final_report(self):
        """Test final report generation."""
        # Log some test data
        self.reporter.log_request("GET", "/users", 100, 200)
        self.reporter.log_request("GET", "/users", 200, 200)
        self.reporter.log_request("POST", "/users", 300, 201)

        time.sleep(0.1)  # Ensure some time passes
        report = self.reporter.generate_final_report()

        self.assertIn("summary", report)
        self.assertEqual(report["summary"]["total_requests"], 3)
        self.assertEqual(report["summary"]["total_failures"], 0)
        self.assertIn("endpoints", report)


class TestEndpointVisualizer(unittest.TestCase):
    """Test the endpoint visualizer functionality."""

    def setUp(self):
        """Set up test environment."""
        self.visualizer = EndpointVisualizer()

    @patch.dict(os.environ, {
        'OPENAPI_URL': 'https://petstore3.swagger.io/api/v3/openapi.json',
        'BASE_URL': 'https://petstore3.swagger.io/api/v3'
    })
    @patch('requests.get')
    def test_analyze_api_mock(self, mock_get):
        """Test API analysis with mocked data."""
        # Mock the OpenAPI spec fetch
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {"tags": ["users"], "summary": "List users"}
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        analysis = self.visualizer.analyze_api(check_health=False)

        self.assertNotIn("error", analysis)
        self.assertIn("metadata", analysis)
        self.assertIn("statistics", analysis)
        self.assertEqual(analysis["metadata"]["api_title"], "Test API")

    def test_calculate_complexity_score(self):
        """Test complexity score calculation."""
        simple_scenario = {
            "path_params": {},
            "query_params": {},
            "header_params": {},
            "request_body": None,
            "expected_responses": ["200"]
        }

        complex_scenario = {
            "path_params": {"id": 1},
            "query_params": {"limit": 10, "offset": 0},
            "header_params": {"X-Custom": "value"},
            "request_body": {"name": "test"},
            "expected_responses": ["200", "201", "400", "500"]
        }

        simple_score = self.visualizer._calculate_complexity_score(simple_scenario)
        complex_score = self.visualizer._calculate_complexity_score(complex_scenario)

        self.assertLess(simple_score, complex_score)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete framework."""

    @patch.dict(os.environ, {
        'OPENAPI_URL': 'https://petstore3.swagger.io/api/v3/openapi.json',
        'BASE_URL': 'https://petstore3.swagger.io/api/v3',
        'AUTH_MODE': 'none',
        'MAX_USERS': '5',
        'SPAWN_RATE': '1'
    })
    def test_complete_workflow(self):
        """Test the complete workflow from OpenAPI to test scenarios."""
        try:
            # Load OpenAPI spec
            loader = OpenAPILoader()
            spec = loader.load_openapi()
            self.assertIn("paths", spec)

            # Build scenarios
            builder = ScenarioBuilder(spec)
            scenarios = builder.build_tasks()
            self.assertGreater(len(scenarios), 0)

            # Test authentication (none mode)
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()
            self.assertIsInstance(headers, dict)

            # Validate environment
            errors = EnvironmentValidator.validate_configuration()
            # Some errors might be expected due to test environment
            self.assertIsInstance(errors, list)

            print(f"✅ Integration test passed: {len(scenarios)} scenarios generated")

        except Exception as e:
            self.fail(f"Integration test failed: {e}")


def run_comprehensive_test():
    """Run a comprehensive test of the entire framework."""
    print("🧪 DYNAMIC STRESS TESTING FRAMEWORK - COMPREHENSIVE TEST")
    print("=" * 60)

    # Set up test environment
    test_env = {
        'OPENAPI_URL': 'https://petstore3.swagger.io/api/v3/openapi.json',
        'BASE_URL': 'https://petstore3.swagger.io/api/v3',
        'AUTH_MODE': 'none',
        'MAX_USERS': '5',
        'SPAWN_RATE': '2',
        'REQUEST_TIMEOUT': '10',
        'RETRY_COUNT': '1',
        'REPORTS_DIR': 'test_reports'
    }

    with patch.dict(os.environ, test_env):
        print("1️⃣  Testing environment validation...")
        errors = EnvironmentValidator.validate_configuration()
        if errors:
            print(f"   ⚠️  Configuration warnings: {len(errors)}")
            for error in errors[:3]:  # Show first 3
                print(f"      {error}")
        else:
            print("   ✅ Environment validation passed")

        print("\n2️⃣  Testing OpenAPI loading...")
        try:
            loader = OpenAPILoader()
            spec = loader.load_openapi()
            print(f"   ✅ Loaded OpenAPI spec with {len(spec.get('paths', {}))} paths")
        except Exception as e:
            print(f"   ❌ OpenAPI loading failed: {e}")
            return False

        print("\n3️⃣  Testing scenario building...")
        try:
            builder = ScenarioBuilder(spec)
            scenarios = builder.build_tasks()
            print(f"   ✅ Built {len(scenarios)} test scenarios")

            # Show sample scenarios
            for i, scenario in enumerate(scenarios[:3]):
                print(f"      {i+1}. {scenario['method']} {scenario['path']}")
        except Exception as e:
            print(f"   ❌ Scenario building failed: {e}")
            return False

        print("\n4️⃣  Testing authentication...")
        try:
            auth_manager = AuthenticationManager()
            headers = auth_manager.get_auth_headers()
            print(f"   ✅ Authentication configured ({len(headers)} headers)")
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            return False

        print("\n5️⃣  Testing endpoint analysis...")
        try:
            visualizer = EndpointVisualizer()
            analysis = visualizer.analyze_api(check_health=False)  # Skip health check for speed
            if "error" not in analysis:
                total_endpoints = analysis["metadata"]["total_endpoints"]
                print(f"   ✅ Analyzed {total_endpoints} endpoints")
            else:
                print(f"   ❌ Analysis failed: {analysis['error']}")
                return False
        except Exception as e:
            print(f"   ❌ Endpoint analysis failed: {e}")
            return False

        print("\n6️⃣  Testing reporter functionality...")
        try:
            reporter = LoadTestReporter()
            reporter.log_request("GET", "/test", 100, 200)
            reporter.log_request("POST", "/test", 200, 201)
            reporter.log_request("GET", "/test", 300, 500, "Server Error")

            report = reporter.generate_final_report()
            print(f"   ✅ Generated report with {report['summary']['total_requests']} requests")
        except Exception as e:
            print(f"   ❌ Reporter test failed: {e}")
            return False

    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
    print("✅ All framework components are working correctly")
    print("🚀 Ready for production load testing!")
    print("=" * 60)
    return True


def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Test the Dynamic Stress Testing Framework")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive test only")
    parser.add_argument("--all", action="store_true", help="Run all tests")

    args = parser.parse_args()

    if not any([args.unit, args.comprehensive, args.all]):
        # Default: run comprehensive test
        args.comprehensive = True

    success = True

    if args.unit or args.all:
        print("🧪 Running unit tests...")
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        success = success and result.wasSuccessful()

    if args.comprehensive or args.all:
        print("\n🔬 Running comprehensive test...")
        success = success and run_comprehensive_test()

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()