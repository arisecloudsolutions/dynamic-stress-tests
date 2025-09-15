import os
import random
import re
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urljoin
import string

class ScenarioBuilder:
    """
    Dynamically builds test scenarios from OpenAPI specifications.
    Generates realistic payloads, handles parameters, and creates executable test tasks.
    """

    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        self.components = spec.get("components", {})
        self.schemas = self.components.get("schemas", {})
        self.fake_data_cache = {}

    def build_tasks(self, include_tags: Optional[str] = None, exclude_tags: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Build executable test tasks from OpenAPI specification.

        Args:
            include_tags: Comma-separated tags to include (e.g., "users,orders")
            exclude_tags: Comma-separated tags to exclude (e.g., "admin,internal")

        Returns:
            List of task dictionaries ready for Locust execution
        """
        include_set = self._parse_tags(include_tags) if include_tags else set()
        exclude_set = self._parse_tags(exclude_tags) if exclude_tags else set()

        paths = self.spec.get("paths", {})
        tasks = []

        print(f"🏗️  Building test scenarios...")
        if include_set:
            print(f"   📌 Including tags: {', '.join(include_set)}")
        if exclude_set:
            print(f"   🚫 Excluding tags: {', '.join(exclude_set)}")

        for path, path_data in paths.items():
            if not isinstance(path_data, dict):
                continue

            for method, operation in path_data.items():
                if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                    continue

                if not isinstance(operation, dict):
                    continue

                # Apply tag filtering
                operation_tags = set(operation.get("tags", []))
                if include_set and not (operation_tags & include_set):
                    continue
                if exclude_set and (operation_tags & exclude_set):
                    continue

                try:
                    task = self._build_single_task(path, method.upper(), operation)
                    if task:
                        tasks.append(task)
                        print(f"   ✅ {method.upper():6} {path:30} [{', '.join(operation_tags) or 'untagged'}]")
                except Exception as e:
                    print(f"   ⚠️  {method.upper():6} {path:30} - Error: {str(e)}")

        print(f"🎯 Built {len(tasks)} executable test scenarios")
        return tasks

    def _build_single_task(self, path: str, method: str, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build a single test task from operation definition."""
        # Extract parameters
        parameters = operation.get("parameters", [])
        path_params = {}
        query_params = {}
        header_params = {}

        for param in parameters:
            if not isinstance(param, dict):
                continue

            name = param.get("name")
            location = param.get("in")
            param_schema = param.get("schema", {})
            required = param.get("required", False)

            if not name:
                continue

            # Generate sample value
            sample_value = self._generate_sample_from_schema(param_schema, name)

            if location == "path":
                path_params[name] = sample_value
            elif location == "query":
                if required or random.random() < 0.7:  # Include 70% of optional query params
                    query_params[name] = sample_value
            elif location == "header":
                header_params[name] = sample_value

        # Generate request body
        request_body = None
        if "requestBody" in operation:
            request_body = self._generate_request_body(operation["requestBody"])

        # Build task
        task = {
            "method": method,
            "path": path,
            "operation_id": operation.get("operationId", f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}"),
            "summary": operation.get("summary", ""),
            "tags": operation.get("tags", []),
            "path_params": path_params,
            "query_params": query_params,
            "header_params": header_params,
            "request_body": request_body,
            "expected_responses": list(operation.get("responses", {}).keys()),
            "weight": self._calculate_task_weight(operation)
        }

        return task

    def _generate_request_body(self, request_body_spec: Dict[str, Any]) -> Optional[Any]:
        """Generate request body from OpenAPI specification."""
        content = request_body_spec.get("content", {})

        # Prioritize JSON content
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
            return self._generate_sample_from_schema(schema)

        # Try other content types
        for content_type, content_spec in content.items():
            if "schema" in content_spec:
                return self._generate_sample_from_schema(content_spec["schema"])

        return None

    def _generate_sample_from_schema(self, schema: Dict[str, Any], field_name: str = "") -> Any:
        """
        Generate realistic sample data from OpenAPI schema.
        Uses field names and formats to create contextually appropriate data.
        """
        if not isinstance(schema, dict):
            return "string"

        # Handle schema references
        if "$ref" in schema:
            ref_schema = self._resolve_schema_ref(schema["$ref"])
            if ref_schema:
                return self._generate_sample_from_schema(ref_schema, field_name)

        # Use example if provided
        if "example" in schema:
            return schema["example"]

        # Use enum if provided
        if "enum" in schema:
            return random.choice(schema["enum"])

        schema_type = schema.get("type", "string")
        schema_format = schema.get("format", "")

        # Generate based on type and format
        if schema_type == "string":
            return self._generate_string_value(schema_format, field_name, schema)
        elif schema_type == "integer":
            return self._generate_integer_value(schema_format, field_name, schema)
        elif schema_type == "number":
            return self._generate_number_value(schema_format, field_name, schema)
        elif schema_type == "boolean":
            return random.choice([True, False])
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            min_items = schema.get("minItems", 1)
            max_items = schema.get("maxItems", 3)
            array_length = random.randint(min_items, max_items)
            return [self._generate_sample_from_schema(items_schema, field_name) for _ in range(array_length)]
        elif schema_type == "object":
            return self._generate_object_value(schema, field_name)
        else:
            return "unknown_type"

    def _generate_string_value(self, format_type: str, field_name: str, schema: Dict[str, Any]) -> str:
        """Generate contextually appropriate string values."""
        field_lower = field_name.lower()

        # Format-based generation
        if format_type == "email":
            return f"test.user{random.randint(1, 999)}@example.com"
        elif format_type == "uri" or format_type == "url":
            return f"https://example.com/resource/{random.randint(1, 1000)}"
        elif format_type == "date":
            date = datetime.now() + timedelta(days=random.randint(-30, 30))
            return date.strftime("%Y-%m-%d")
        elif format_type == "date-time":
            date = datetime.now() + timedelta(hours=random.randint(-72, 72))
            return date.isoformat() + "Z"
        elif format_type == "uuid":
            return f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}-4{random.randint(100, 999)}-a{random.randint(100, 999)}-{random.randint(100000000000, 999999999999)}"
        elif format_type == "password":
            return "Test123!@#"

        # Field name-based generation
        if any(keyword in field_lower for keyword in ["email", "mail"]):
            return f"user{random.randint(1, 999)}@example.com"
        elif any(keyword in field_lower for keyword in ["name", "title"]):
            names = ["John Doe", "Jane Smith", "Test User", "Sample Data", "Demo Account"]
            return random.choice(names)
        elif any(keyword in field_lower for keyword in ["id", "uuid"]):
            return str(random.randint(1, 10000))
        elif any(keyword in field_lower for keyword in ["phone", "tel"]):
            return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        elif any(keyword in field_lower for keyword in ["address", "street"]):
            return f"{random.randint(1, 999)} Test Street, Example City"
        elif any(keyword in field_lower for keyword in ["description", "comment", "note"]):
            return f"Test description generated at {datetime.now().strftime('%H:%M:%S')}"
        elif any(keyword in field_lower for keyword in ["status", "state"]):
            return random.choice(["active", "pending", "completed", "draft"])

        # Schema constraints
        min_length = schema.get("minLength", 1)
        max_length = schema.get("maxLength", 20)
        length = random.randint(min_length, min(max_length, 50))

        if schema.get("pattern"):
            # For patterns, generate simple alphanumeric string
            return "test" + "".join(random.choices(string.ascii_lowercase + string.digits, k=max(0, length-4)))

        return f"test_string_{random.randint(1, 999)}"

    def _generate_integer_value(self, format_type: str, field_name: str, schema: Dict[str, Any]) -> int:
        """Generate appropriate integer values."""
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 1000)

        field_lower = field_name.lower()

        if any(keyword in field_lower for keyword in ["id", "count", "number"]):
            return random.randint(max(1, minimum), min(maximum, 10000))
        elif any(keyword in field_lower for keyword in ["age"]):
            return random.randint(max(18, minimum), min(maximum, 100))
        elif any(keyword in field_lower for keyword in ["year"]):
            return random.randint(max(2020, minimum), min(maximum, 2030))

        return random.randint(minimum, maximum)

    def _generate_number_value(self, format_type: str, field_name: str, schema: Dict[str, Any]) -> float:
        """Generate appropriate number values."""
        minimum = schema.get("minimum", 0.0)
        maximum = schema.get("maximum", 1000.0)

        field_lower = field_name.lower()

        if any(keyword in field_lower for keyword in ["price", "cost", "amount"]):
            return round(random.uniform(max(0.01, minimum), min(maximum, 999.99)), 2)
        elif any(keyword in field_lower for keyword in ["rate", "percent"]):
            return round(random.uniform(max(0.0, minimum), min(maximum, 1.0)), 3)

        return round(random.uniform(minimum, maximum), 2)

    def _generate_object_value(self, schema: Dict[str, Any], field_name: str = "") -> Dict[str, Any]:
        """Generate object with all properties."""
        properties = schema.get("properties", {})
        required_props = set(schema.get("required", []))
        result = {}

        for prop_name, prop_schema in properties.items():
            # Include all required properties + 70% of optional ones
            if prop_name in required_props or random.random() < 0.7:
                result[prop_name] = self._generate_sample_from_schema(prop_schema, prop_name)

        return result

    def _resolve_schema_ref(self, ref: str) -> Optional[Dict[str, Any]]:
        """Resolve $ref to actual schema definition."""
        if not ref.startswith("#/"):
            return None

        parts = ref[2:].split("/")
        current = self.spec

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current if isinstance(current, dict) else None

    def _calculate_task_weight(self, operation: Dict[str, Any]) -> int:
        """Calculate task weight based on operation characteristics."""
        weight = 1

        # Higher weight for GET operations (more common in load testing)
        if operation.get("method", "").upper() == "GET":
            weight += 2

        # Higher weight for operations with common tags
        tags = operation.get("tags", [])
        common_tags = ["public", "core", "main", "primary"]
        if any(tag.lower() in common_tags for tag in tags):
            weight += 1

        # Lower weight for admin/internal operations
        admin_tags = ["admin", "internal", "debug", "test"]
        if any(tag.lower() in admin_tags for tag in tags):
            weight = max(1, weight - 2)

        return weight

    def _parse_tags(self, tags_string: str) -> set:
        """Parse comma-separated tags string into set."""
        if not tags_string:
            return set()
        return {tag.strip() for tag in tags_string.split(",") if tag.strip()}

    def get_scenario_summary(self) -> Dict[str, Any]:
        """Get summary of generated scenarios for reporting."""
        include_tags = os.getenv("SPEC_INCLUDE_TAGS", "")
        exclude_tags = os.getenv("SPEC_EXCLUDE_TAGS", "")

        tasks = self.build_tasks(include_tags, exclude_tags)

        methods_count = {}
        tags_count = {}
        total_weight = 0

        for task in tasks:
            method = task["method"]
            methods_count[method] = methods_count.get(method, 0) + 1

            for tag in task["tags"]:
                tags_count[tag] = tags_count.get(tag, 0) + 1

            total_weight += task["weight"]

        return {
            "total_scenarios": len(tasks),
            "methods_distribution": methods_count,
            "tags_distribution": tags_count,
            "total_weight": total_weight,
            "filtering": {
                "include_tags": include_tags,
                "exclude_tags": exclude_tags
            }
        }


def build_tasks(spec: Dict[str, Any], include_tags: Optional[str] = None, exclude_tags: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to build test tasks from OpenAPI specification.

    Args:
        spec: OpenAPI specification dictionary
        include_tags: Comma-separated tags to include
        exclude_tags: Comma-separated tags to exclude

    Returns:
        List of executable test tasks
    """
    builder = ScenarioBuilder(spec)
    return builder.build_tasks(include_tags, exclude_tags)


if __name__ == "__main__":
    # Test with Swagger Petstore
    import requests

    print("🧪 Testing ScenarioBuilder with Swagger Petstore...")
    response = requests.get("https://petstore3.swagger.io/api/v3/openapi.json")
    spec = response.json()

    builder = ScenarioBuilder(spec)
    tasks = builder.build_tasks()

    print(f"\n📊 Generated {len(tasks)} test scenarios")
    for i, task in enumerate(tasks[:5]):  # Show first 5
        print(f"  {i+1}. {task['method']} {task['path']} - {task['summary']}")

    summary = builder.get_scenario_summary()
    print(f"\n📈 Summary: {summary}")