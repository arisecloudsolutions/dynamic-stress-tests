import os
import json
import requests
import yaml
from typing import Dict, Any, Optional
from urllib.parse import urlparse

class OpenAPILoader:
    """
    Loads and validates OpenAPI specifications from URL or local file.
    Provides detailed feedback and error handling.
    """

    def __init__(self):
        self.spec_data: Optional[Dict[str, Any]] = None
        self.source: Optional[str] = None
        self.validation_results: Dict[str, Any] = {}

    def load_openapi(self) -> Dict[str, Any]:
        """
        Load OpenAPI specification with comprehensive error handling and validation.

        Returns:
            Dict containing the parsed OpenAPI specification

        Raises:
            RuntimeError: If loading fails or validation errors occur
        """
        path = os.getenv("OPENAPI_PATH")
        url = os.getenv("OPENAPI_URL")

        if not path and not url:
            raise RuntimeError(
                "❌ Configuration Error: Either OPENAPI_URL or OPENAPI_PATH must be provided\n"
                "   Set one of these environment variables:\n"
                "   - OPENAPI_URL=https://api.example.com/openapi.json\n"
                "   - OPENAPI_PATH=/path/to/openapi.json"
            )

        try:
            if path:
                self.spec_data = self._load_from_file(path)
                self.source = f"file://{path}"
            else:
                self.spec_data = self._load_from_url(url)
                self.source = url

            self._validate_specification()
            self._print_discovery_summary()

            return self.spec_data

        except Exception as e:
            print(f"❌ OpenAPI Loading Failed: {str(e)}")
            raise

    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load OpenAPI spec from local file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"OpenAPI file not found: {file_path}")

        print(f"📁 Loading OpenAPI spec from: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try JSON first, then YAML
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid JSON/YAML format: {e}")

    def _load_from_url(self, url: str) -> Dict[str, Any]:
        """Load OpenAPI spec from URL with detailed feedback."""
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL format: {url}")

        print(f"🌐 Fetching OpenAPI spec from: {url}")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            print(f"✅ Successfully fetched spec ({len(response.content)} bytes)")

            # Try JSON first, then YAML
            try:
                return response.json()
            except json.JSONDecodeError:
                try:
                    return yaml.safe_load(response.text)
                except yaml.YAMLError as e:
                    raise ValueError(f"Response is not valid JSON/YAML: {e}")

        except requests.exceptions.Timeout:
            raise RuntimeError(f"Timeout fetching OpenAPI spec from {url}")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"Connection error fetching OpenAPI spec from {url}")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"HTTP error {response.status_code} fetching OpenAPI spec: {e}")

    def _validate_specification(self):
        """Validate OpenAPI specification structure."""
        if not isinstance(self.spec_data, dict):
            raise ValueError("OpenAPI specification must be a JSON object")

        # Check for required OpenAPI fields
        if "openapi" not in self.spec_data and "swagger" not in self.spec_data:
            raise ValueError("Missing 'openapi' or 'swagger' version field")

        if "paths" not in self.spec_data:
            raise ValueError("OpenAPI specification missing 'paths' section")

        if not self.spec_data["paths"]:
            raise ValueError("OpenAPI specification has empty 'paths' section")

        # Store validation results
        self.validation_results = {
            "version": self.spec_data.get("openapi") or self.spec_data.get("swagger"),
            "title": self.spec_data.get("info", {}).get("title", "Unknown API"),
            "description": self.spec_data.get("info", {}).get("description", ""),
            "servers": self.spec_data.get("servers", []),
            "total_paths": len(self.spec_data["paths"]),
            "total_operations": self._count_operations(),
            "tags": self._extract_tags(),
            "security_schemes": self._extract_security_schemes()
        }

        print("✅ OpenAPI specification validation passed")

    def _count_operations(self) -> int:
        """Count total HTTP operations in the spec."""
        count = 0
        for path_data in self.spec_data["paths"].values():
            if isinstance(path_data, dict):
                for method in ["get", "post", "put", "patch", "delete", "head", "options"]:
                    if method in path_data:
                        count += 1
        return count

    def _extract_tags(self) -> list:
        """Extract all unique tags from operations."""
        tags = set()
        for path_data in self.spec_data["paths"].values():
            if isinstance(path_data, dict):
                for method_data in path_data.values():
                    if isinstance(method_data, dict) and "tags" in method_data:
                        tags.update(method_data["tags"])
        return sorted(list(tags))

    def _extract_security_schemes(self) -> list:
        """Extract security scheme types."""
        components = self.spec_data.get("components", {})
        security_schemes = components.get("securitySchemes", {})
        return [scheme.get("type") for scheme in security_schemes.values()]

    def _print_discovery_summary(self):
        """Print a beautiful summary of discovered endpoints."""
        results = self.validation_results

        print("\n" + "="*60)
        print("🔍 OPENAPI DISCOVERY SUMMARY")
        print("="*60)
        print(f"📋 API Title: {results['title']}")
        print(f"📝 Version: {results['version']}")
        print(f"🔗 Source: {self.source}")
        print(f"📊 Total Paths: {results['total_paths']}")
        print(f"🎯 Total Operations: {results['total_operations']}")

        if results['tags']:
            print(f"🏷️  Available Tags: {', '.join(results['tags'])}")

        if results['security_schemes']:
            print(f"🔐 Security Types: {', '.join(set(results['security_schemes']))}")

        print("\n📍 DISCOVERED ENDPOINTS:")
        print("-" * 40)

        for path, path_data in self.spec_data["paths"].items():
            if isinstance(path_data, dict):
                methods = []
                for method in ["get", "post", "put", "patch", "delete"]:
                    if method in path_data:
                        operation = path_data[method]
                        tags = operation.get("tags", ["untagged"])
                        methods.append(f"{method.upper()}({','.join(tags)})")

                if methods:
                    print(f"  {path:30} → {' | '.join(methods)}")

        print("="*60)
        print("✅ Ready for load testing!")
        print("="*60 + "\n")

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def get_endpoint_summary(self) -> Dict[str, Any]:
        """Get a summary of endpoints for external tools."""
        if not self.spec_data:
            return {}

        return {
            "source": self.source,
            "validation_results": self.validation_results,
            "endpoints": self._get_endpoint_details()
        }

    def _get_endpoint_details(self) -> list:
        """Get detailed endpoint information."""
        endpoints = []

        for path, path_data in self.spec_data["paths"].items():
            if isinstance(path_data, dict):
                for method, operation in path_data.items():
                    if method.lower() in ["get", "post", "put", "patch", "delete"] and isinstance(operation, dict):
                        endpoints.append({
                            "path": path,
                            "method": method.upper(),
                            "summary": operation.get("summary", ""),
                            "tags": operation.get("tags", []),
                            "operationId": operation.get("operationId", ""),
                            "parameters": len(operation.get("parameters", [])),
                            "has_request_body": "requestBody" in operation,
                            "responses": list(operation.get("responses", {}).keys())
                        })

        return endpoints


def load_openapi() -> Dict[str, Any]:
    """
    Convenience function to load OpenAPI specification.

    Returns:
        Dict containing the parsed OpenAPI specification
    """
    loader = OpenAPILoader()
    return loader.load_openapi()


if __name__ == "__main__":
    # Test the loader with Swagger Petstore
    os.environ["OPENAPI_URL"] = "https://petstore3.swagger.io/api/v3/openapi.json"
    try:
        spec = load_openapi()
        print(f"✅ Successfully loaded spec with {len(spec['paths'])} paths")
    except Exception as e:
        print(f"❌ Error: {e}")