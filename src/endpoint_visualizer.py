#!/usr/bin/env python3
"""
Endpoint Discovery and Visualization Tool

This standalone script analyzes OpenAPI specifications and provides
visual feedback about discovered endpoints, their status, and test coverage.
Perfect for developers to understand what will be tested before running load tests.
"""

import os
import sys
import json
import requests
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openapi_loader import OpenAPILoader
from scenario_builder import ScenarioBuilder
from auth import AuthenticationManager
from utils import EndpointHealthChecker, EnvironmentValidator


class EndpointVisualizer:
    """
    Provides visual representation and analysis of API endpoints
    discovered from OpenAPI specifications.
    """

    def __init__(self):
        self.spec_data: Optional[Dict[str, Any]] = None
        self.scenarios: List[Dict[str, Any]] = []
        self.health_results: Dict[str, Any] = {}
        self.auth_headers: Dict[str, str] = {}

    def analyze_api(self, include_tags: str = "", exclude_tags: str = "", check_health: bool = True) -> Dict[str, Any]:
        """
        Complete analysis of API endpoints with visualization.

        Args:
            include_tags: Comma-separated tags to include
            exclude_tags: Comma-separated tags to exclude
            check_health: Whether to perform health checks

        Returns:
            Complete analysis results
        """
        print("🔍 DYNAMIC API ENDPOINT ANALYSIS")
        print("=" * 60)

        try:
            # Load OpenAPI specification
            print("1️⃣  Loading OpenAPI specification...")
            loader = OpenAPILoader()
            self.spec_data = loader.load_openapi()

            # Build scenarios
            print("\n2️⃣  Building test scenarios...")
            builder = ScenarioBuilder(self.spec_data)
            self.scenarios = builder.build_tasks(include_tags, exclude_tags)

            # Setup authentication if needed
            if os.getenv("AUTH_MODE"):
                print("\n3️⃣  Setting up authentication...")
                auth_manager = AuthenticationManager()
                self.auth_headers = auth_manager.get_auth_headers()

            # Health check
            if check_health and os.getenv("BASE_URL"):
                print("\n4️⃣  Performing endpoint health checks...")
                self._perform_health_checks()

            # Generate visualizations
            print("\n5️⃣  Generating endpoint visualizations...")
            analysis_results = self._generate_analysis()

            self._print_visual_summary(analysis_results)
            self._save_analysis_report(analysis_results)

            return analysis_results

        except Exception as e:
            print(f"💀 Analysis failed: {e}")
            return {"error": str(e)}

    def _perform_health_checks(self):
        """Perform health checks on discovered endpoints."""
        base_url = os.getenv("BASE_URL", "")
        if not base_url:
            print("   ⚠️  No BASE_URL set, skipping health checks")
            return

        checker = EndpointHealthChecker(base_url, self.auth_headers)

        # Basic connectivity
        if not checker.check_base_connectivity():
            print("   💀 Base URL not accessible")
            return

        # Sample endpoint checks
        self.health_results = checker.sample_endpoint_check(self.scenarios, max_checks=10)

    def _generate_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis of the API."""
        if not self.spec_data or not self.scenarios:
            return {}

        # Categorize endpoints
        methods_stats = {}
        tags_stats = {}
        auth_requirements = {}
        parameter_complexity = {}

        for scenario in self.scenarios:
            method = scenario["method"]
            tags = scenario.get("tags", ["untagged"])

            # Method statistics
            methods_stats[method] = methods_stats.get(method, 0) + 1

            # Tag statistics
            for tag in tags:
                tags_stats[tag] = tags_stats.get(tag, 0) + 1

            # Parameter complexity analysis
            path_params = len(scenario.get("path_params", {}))
            query_params = len(scenario.get("query_params", {}))
            has_body = scenario.get("request_body") is not None

            complexity_score = path_params + query_params + (2 if has_body else 0)
            complexity_level = "Low" if complexity_score <= 2 else "Medium" if complexity_score <= 5 else "High"

            parameter_complexity[complexity_level] = parameter_complexity.get(complexity_level, 0) + 1

        # Generate endpoint matrix
        endpoint_matrix = self._generate_endpoint_matrix()

        # Generate test coverage analysis
        coverage_analysis = self._generate_coverage_analysis()

        return {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "total_endpoints": len(self.scenarios),
                "api_title": self.spec_data.get("info", {}).get("title", "Unknown API"),
                "api_version": self.spec_data.get("info", {}).get("version", "Unknown"),
                "openapi_version": self.spec_data.get("openapi", self.spec_data.get("swagger", "Unknown")),
                "base_url": os.getenv("BASE_URL", "Not configured")
            },
            "statistics": {
                "methods_distribution": methods_stats,
                "tags_distribution": tags_stats,
                "parameter_complexity": parameter_complexity
            },
            "endpoint_matrix": endpoint_matrix,
            "coverage_analysis": coverage_analysis,
            "health_check_results": self.health_results,
            "scenarios": self.scenarios
        }

    def _generate_endpoint_matrix(self) -> List[Dict[str, Any]]:
        """Generate a matrix view of all endpoints with their characteristics."""
        matrix = []

        for scenario in self.scenarios:
            entry = {
                "path": scenario["path"],
                "method": scenario["method"],
                "tags": scenario.get("tags", []),
                "summary": scenario.get("summary", ""),
                "parameters": {
                    "path": len(scenario.get("path_params", {})),
                    "query": len(scenario.get("query_params", {})),
                    "headers": len(scenario.get("header_params", {}))
                },
                "has_request_body": scenario.get("request_body") is not None,
                "expected_responses": scenario.get("expected_responses", []),
                "weight": scenario.get("weight", 1),
                "complexity_score": self._calculate_complexity_score(scenario)
            }
            matrix.append(entry)

        # Sort by method then path
        matrix.sort(key=lambda x: (x["method"], x["path"]))
        return matrix

    def _calculate_complexity_score(self, scenario: Dict[str, Any]) -> int:
        """Calculate complexity score for an endpoint."""
        score = 0
        score += len(scenario.get("path_params", {})) * 2  # Path params are critical
        score += len(scenario.get("query_params", {}))
        score += len(scenario.get("header_params", {}))
        score += 3 if scenario.get("request_body") else 0  # Request body adds complexity
        score += len(scenario.get("expected_responses", [])) // 2  # Multiple responses
        return score

    def _generate_coverage_analysis(self) -> Dict[str, Any]:
        """Analyze test coverage across different dimensions."""
        if not self.scenarios:
            return {}

        # HTTP method coverage
        all_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
        covered_methods = {scenario["method"] for scenario in self.scenarios}
        method_coverage = (len(covered_methods) / len(all_methods)) * 100

        # Tag coverage
        all_tags = set()
        for path_data in self.spec_data.get("paths", {}).values():
            for operation in path_data.values():
                if isinstance(operation, dict) and "tags" in operation:
                    all_tags.update(operation["tags"])

        covered_tags = set()
        for scenario in self.scenarios:
            covered_tags.update(scenario.get("tags", []))

        tag_coverage = (len(covered_tags) / len(all_tags) * 100) if all_tags else 100

        # Parameter type coverage
        param_types = {"path", "query", "header", "body"}
        covered_param_types = set()

        for scenario in self.scenarios:
            if scenario.get("path_params"):
                covered_param_types.add("path")
            if scenario.get("query_params"):
                covered_param_types.add("query")
            if scenario.get("header_params"):
                covered_param_types.add("header")
            if scenario.get("request_body"):
                covered_param_types.add("body")

        param_coverage = (len(covered_param_types) / len(param_types)) * 100

        return {
            "method_coverage": {
                "percentage": method_coverage,
                "covered": list(covered_methods),
                "missing": list(all_methods - covered_methods)
            },
            "tag_coverage": {
                "percentage": tag_coverage,
                "covered": list(covered_tags),
                "missing": list(all_tags - covered_tags)
            },
            "parameter_coverage": {
                "percentage": param_coverage,
                "covered": list(covered_param_types),
                "missing": list(param_types - covered_param_types)
            }
        }

    def _print_visual_summary(self, analysis: Dict[str, Any]):
        """Print a beautiful visual summary of the analysis."""
        if "error" in analysis:
            return

        metadata = analysis["metadata"]
        stats = analysis["statistics"]
        coverage = analysis["coverage_analysis"]

        print("\n" + "="*60)
        print("📊 ENDPOINT ANALYSIS SUMMARY")
        print("="*60)

        # API Information
        print(f"📋 API: {metadata['api_title']} (v{metadata['api_version']})")
        print(f"🔗 Base URL: {metadata['base_url']}")
        print(f"📄 OpenAPI: {metadata['openapi_version']}")
        print(f"🎯 Total Endpoints: {metadata['total_endpoints']}")

        # Method Distribution
        print(f"\n🔧 METHOD DISTRIBUTION:")
        for method, count in sorted(stats['methods_distribution'].items()):
            bar = "█" * min(count, 20)
            print(f"   {method:7} │ {bar:<20} │ {count:3d}")

        # Tag Distribution (top 10)
        if stats['tags_distribution']:
            print(f"\n🏷️  TOP TAGS:")
            sorted_tags = sorted(stats['tags_distribution'].items(), key=lambda x: x[1], reverse=True)
            for tag, count in sorted_tags[:10]:
                bar = "█" * min(count, 15)
                print(f"   {tag[:15]:15} │ {bar:<15} │ {count:3d}")

        # Complexity Distribution
        print(f"\n🧩 COMPLEXITY DISTRIBUTION:")
        for level, count in stats['parameter_complexity'].items():
            bar = "█" * min(count, 20)
            print(f"   {level:7} │ {bar:<20} │ {count:3d}")

        # Coverage Analysis
        print(f"\n📈 TEST COVERAGE:")
        method_cov = coverage.get('method_coverage', {}).get('percentage', 0)
        tag_cov = coverage.get('tag_coverage', {}).get('percentage', 0)
        param_cov = coverage.get('parameter_coverage', {}).get('percentage', 0)

        print(f"   Methods:    {method_cov:5.1f}% {'✅' if method_cov > 80 else '⚠️' if method_cov > 50 else '💀'}")
        print(f"   Tags:       {tag_cov:5.1f}% {'✅' if tag_cov > 80 else '⚠️' if tag_cov > 50 else '💀'}")
        print(f"   Parameters: {param_cov:5.1f}% {'✅' if param_cov > 80 else '⚠️' if param_cov > 50 else '💀'}")

        # Health Check Results
        if self.health_results and self.health_results.get('checked', 0) > 0:
            health_rate = (self.health_results['accessible'] / self.health_results['checked']) * 100
            print(f"\n🏥 HEALTH CHECK:")
            print(f"   Endpoints:  {self.health_results['accessible']}/{self.health_results['checked']} accessible ({health_rate:.1f}%)")

            if health_rate < 50:
                print("   ⚠️  Low endpoint accessibility - check authentication or network connectivity")
            elif health_rate < 80:
                print("   ⚠️  Some endpoints may have issues")
            else:
                print("   ✅ Good endpoint accessibility")

        # Endpoint Matrix (top 10 most complex)
        matrix = analysis.get('endpoint_matrix', [])
        if matrix:
            print(f"\n🎯 TOP COMPLEX ENDPOINTS:")
            complex_endpoints = sorted(matrix, key=lambda x: x['complexity_score'], reverse=True)[:10]

            for ep in complex_endpoints:
                complexity_bar = "█" * min(ep['complexity_score'], 10)
                tags_str = ",".join(ep['tags'][:2]) if ep['tags'] else 'untagged'
                print(f"   {ep['method']:6} {ep['path'][:35]:35} │ {complexity_bar:<10} │ {tags_str}")

        print("\n" + "="*60)
        print("✅ Analysis complete! Check 'endpoint_analysis.json' for full details.")
        print("="*60)

    def _save_analysis_report(self, analysis: Dict[str, Any]):
        """Save detailed analysis report to JSON file."""
        reports_dir = os.getenv("REPORTS_DIR", "reports")
        os.makedirs(reports_dir, exist_ok=True)

        filepath = os.path.join(reports_dir, "endpoint_analysis.json")
        with open(filepath, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"📄 Detailed analysis saved: {filepath}")

    def generate_html_report(self, analysis: Dict[str, Any], output_file: str = "endpoint_report.html"):
        """Generate an HTML report with visual charts and tables."""
        if "error" in analysis:
            return

        html_content = self._generate_html_content(analysis)

        reports_dir = os.getenv("REPORTS_DIR", "reports")
        os.makedirs(reports_dir, exist_ok=True)

        filepath = os.path.join(reports_dir, output_file)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"🌐 HTML report generated: {filepath}")

    def _generate_html_content(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML content for the visual report."""
        metadata = analysis["metadata"]
        stats = analysis["statistics"]
        matrix = analysis.get("endpoint_matrix", [])

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Endpoint Analysis - {metadata['api_title']}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .endpoint-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .endpoint-table th, .endpoint-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .endpoint-table th {{ background-color: #007bff; color: white; }}
        .method-badge {{ padding: 2px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.8em; }}
        .method-get {{ background-color: #28a745; }}
        .method-post {{ background-color: #007bff; }}
        .method-put {{ background-color: #ffc107; color: black; }}
        .method-patch {{ background-color: #17a2b8; }}
        .method-delete {{ background-color: #dc3545; }}
        .complexity-bar {{ display: inline-block; background: #e9ecef; width: 100px; height: 20px; border-radius: 10px; }}
        .complexity-fill {{ height: 100%; background: linear-gradient(to right, #28a745, #ffc107, #dc3545); border-radius: 10px; }}
        .tag-list {{ font-size: 0.8em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 API Endpoint Analysis</h1>
            <h2>{metadata['api_title']} (v{metadata['api_version']})</h2>
            <p><strong>Base URL:</strong> {metadata['base_url']}</p>
            <p><strong>Analysis Date:</strong> {metadata['analysis_timestamp'][:19]}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 Total Endpoints</h3>
                <div style="font-size: 2em; font-weight: bold; color: #007bff;">{metadata['total_endpoints']}</div>
            </div>
            <div class="stat-card">
                <h3>🔧 HTTP Methods</h3>
                <div style="font-size: 1.2em;">{len(stats['methods_distribution'])} different methods</div>
            </div>
            <div class="stat-card">
                <h3>🏷️ Tags</h3>
                <div style="font-size: 1.2em;">{len(stats['tags_distribution'])} categories</div>
            </div>
        </div>

        <h3>🎯 Endpoint Details</h3>
        <table class="endpoint-table">
            <thead>
                <tr>
                    <th>Method</th>
                    <th>Path</th>
                    <th>Tags</th>
                    <th>Parameters</th>
                    <th>Complexity</th>
                    <th>Summary</th>
                </tr>
            </thead>
            <tbody>
        """

        for endpoint in matrix:
            method_class = f"method-{endpoint['method'].lower()}"
            param_count = endpoint['parameters']['path'] + endpoint['parameters']['query'] + endpoint['parameters']['headers']
            complexity_percentage = min(endpoint['complexity_score'] * 10, 100)
            tags_display = ', '.join(endpoint['tags'][:3]) if endpoint['tags'] else 'untagged'

            html += f"""
                <tr>
                    <td><span class="method-badge {method_class}">{endpoint['method']}</span></td>
                    <td><code>{endpoint['path']}</code></td>
                    <td class="tag-list">{tags_display}</td>
                    <td>{param_count} params</td>
                    <td>
                        <div class="complexity-bar">
                            <div class="complexity-fill" style="width: {complexity_percentage}%"></div>
                        </div>
                        <small>({endpoint['complexity_score']})</small>
                    </td>
                    <td>{endpoint['summary'][:50]}{'...' if len(endpoint['summary']) > 50 else ''}</td>
                </tr>
            """

        html += """
            </tbody>
        </table>

        <div style="margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 8px;">
            <h4>💡 Analysis Notes</h4>
            <ul>
                <li><strong>Complexity Score:</strong> Based on number of parameters, request body presence, and response variety</li>
                <li><strong>Green methods (GET):</strong> Read operations, typically safe for high-frequency testing</li>
                <li><strong>Blue methods (POST/PATCH):</strong> Write operations, use with caution in load testing</li>
                <li><strong>Red methods (DELETE):</strong> Destructive operations, typically excluded from load testing</li>
            </ul>
        </div>
    </div>
</body>
</html>
        """

        return html


def main():
    """Main CLI interface for the endpoint visualizer."""
    parser = argparse.ArgumentParser(
        description="Analyze and visualize API endpoints from OpenAPI specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis with health checks
  python endpoint_visualizer.py

  # Analyze specific tags only
  python endpoint_visualizer.py --include-tags "users,orders" --exclude-tags "admin"

  # Skip health checks (faster)
  python endpoint_visualizer.py --no-health-check

  # Generate HTML report
  python endpoint_visualizer.py --html

Environment Variables:
  OPENAPI_URL     - URL to OpenAPI specification
  OPENAPI_PATH    - Path to local OpenAPI file
  BASE_URL        - API base URL for health checks
  AUTH_MODE       - Authentication mode (jwt, login, apikey, etc.)
        """
    )

    parser.add_argument(
        "--include-tags",
        help="Comma-separated list of tags to include"
    )
    parser.add_argument(
        "--exclude-tags",
        help="Comma-separated list of tags to exclude"
    )
    parser.add_argument(
        "--no-health-check",
        action="store_true",
        help="Skip endpoint health checks (faster analysis)"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report in addition to console output"
    )

    args = parser.parse_args()

    # Validate environment
    errors = EnvironmentValidator.validate_configuration()
    if errors:
        print("💀 Configuration errors found:")
        for error in errors:
            print(f"   {error}")
        print("\n💡 Please fix the configuration and try again.")
        sys.exit(1)

    # Run analysis
    visualizer = EndpointVisualizer()
    analysis = visualizer.analyze_api(
        include_tags=args.include_tags or "",
        exclude_tags=args.exclude_tags or "",
        check_health=not args.no_health_check
    )

    if "error" in analysis:
        print(f"💀 Analysis failed: {analysis['error']}")
        sys.exit(1)

    # Generate HTML report if requested
    if args.html:
        visualizer.generate_html_report(analysis)

    print("\n Ready to run load tests with these endpoints!")
    print("   Use: docker compose up --build")


if __name__ == "__main__":
    main()