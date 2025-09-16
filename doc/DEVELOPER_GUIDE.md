# Developer Guide - Dynamic Stress Testing Framework

##  Quick Start for Developers

### 1. Get Started in 30 Seconds

```bash
# Clone and enter the project
git clone <repo-url>
cd dynamic-stress-tests

# Quick demo with public API
python3 src/quick_start.py

# Or copy example config and run
cp examples/.env.petstore .env
docker compose up --build
# Open http://localhost:8089
```

## 🏗️ Project Structure

```
dynamic-stress-tests/
├── src/                     # Source code
│   ├── __init__.py         # Package initialization
│   ├── auth.py             # Authentication manager
│   ├── config_validator.py # Configuration validation
│   ├── debug_utils.py      # Development utilities
│   ├── exceptions.py       # Custom exceptions
│   ├── locustfile.py       # Main Locust test file
│   ├── logger.py           # Logging configuration
│   ├── openapi_loader.py   # OpenAPI spec loading
│   ├── scenario_builder.py # Test scenario generation
│   ├── settings.py         # Framework settings
│   └── utils.py            # Utility functions
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Pytest configuration
│   ├── test_auth.py        # Authentication tests
│   └── test_config_validator.py # Configuration tests
├── doc/                    # Documentation
│   ├── CLAUDE.md           # Project requirements
│   ├── DEVELOPER_GUIDE.md  # This file
│   └── PARAMETERS.md       # Parameter documentation
├── examples/               # Example configurations
├── reports/                # Generated reports
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Container orchestration
└── Makefile               # Development commands
```

### 2. Test Your Own API

```bash
# Interactive setup
python3 quick_start.py

# Or manually configure
cp examples/.env.jwt_api .env
# Edit .env with your API details
docker compose up --build
```

## 📋 Configuration Examples

### Example 1: Public API (No Auth)
```env
OPENAPI_URL=https://petstore3.swagger.io/api/v3/openapi.json
BASE_URL=https://petstore3.swagger.io/api/v3
AUTH_MODE=none
MAX_USERS=20
SPAWN_RATE=3
```

### Example 2: JWT Authentication
```env
OPENAPI_URL=https://your-api.com/openapi.json
BASE_URL=https://your-api.com
AUTH_MODE=jwt
JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your.token
MAX_USERS=50
SPAWN_RATE=5
SPEC_EXCLUDE_TAGS=admin,delete
```

### Example 3: Login Flow
```env
OPENAPI_URL=https://staging-api.com/openapi.json
BASE_URL=https://staging-api.com
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=test@example.com
LOGIN_PASS=testpassword
MAX_USERS=25
SPAWN_RATE=2
```

### Example 4: Production-Safe Testing
```env
OPENAPI_URL=https://api.yourcompany.com/openapi.json
BASE_URL=https://api.yourcompany.com
AUTH_MODE=apikey
API_KEY=your-production-api-key

# CONSERVATIVE SETTINGS
MAX_USERS=5
SPAWN_RATE=1
RUN_TIME=1m

# SAFETY FIRST - READ ONLY
SPEC_INCLUDE_TAGS=read,get,list
SPEC_EXCLUDE_TAGS=write,post,put,delete,admin
```

## 🔧 Common Configuration Problems & Solutions

### Problem: "No OpenAPI source configured"
```bash
# Solution: Set either URL or path
export OPENAPI_URL=https://api.example.com/openapi.json
# OR
export OPENAPI_PATH=/path/to/openapi.json
```

### Problem: "Authentication failed"
```bash
# For JWT issues:
export AUTH_MODE=jwt
export JWT_TOKEN=your.actual.jwt.token

# For login issues:
export AUTH_MODE=login
export LOGIN_URL=/api/auth/login  # Check exact endpoint
export LOGIN_USER=your@email.com
export LOGIN_PASS=yourpassword
```

### Problem: "No test scenarios generated"
```bash
# Check tag filters
unset SPEC_INCLUDE_TAGS
unset SPEC_EXCLUDE_TAGS

# Or analyze first
python3 src/endpoint_visualizer.py --no-health-check
```

### Problem: "Docker issues"
```bash
# Check Docker is running
docker --version
docker info

# Restart if needed
docker compose down
docker compose up --build
```

## 🎯 Testing Scenarios

### Safe Production Testing
```bash
# Use production-safe template
cp examples/.env.production_safe .env
# Edit with your values
# Start with 1 user, short duration
MAX_USERS=1 RUN_TIME=30s docker compose run --rm locust
```

### Staging Environment
```bash
# Use full testing template
cp examples/.env.login_flow .env
# Edit with staging credentials
docker compose up --build
```

### Local Development
```bash
# Terminal 1: Start mock server
python3 tests/mock_api_server.py

# Terminal 2: Test against mock
cp examples/.env.mock_server .env
docker compose up --build
```

### Spike Testing
```bash
# Quick spike test
./scenarios/spike_test.sh

# Custom spike
SPIKE_USERS=200 SPIKE_RATE=100 SPIKE_DURATION=3m ./scenarios/spike_test.sh
```

### Endurance Testing
```bash
# Long-running test
./scenarios/soak_test.sh

# Custom soak
SOAK_USERS=30 SOAK_DURATION=2h ./scenarios/soak_test.sh
```

## 🔍 Analysis & Debugging

### Endpoint Discovery
```bash
# Analyze any API
OPENAPI_URL=https://api.example.com/openapi.json python3 endpoint_visualizer.py

# Generate HTML report
python3 endpoint_visualizer.py --html

# Skip health checks (faster)
python3 endpoint_visualizer.py --no-health-check
```

### Health Checks
```bash
# Quick system check
python3 scenarios/troubleshoot.py --quick

# Full diagnostics
python3 scenarios/troubleshoot.py
```

### Configuration Validation
```bash
# Test current config
python3 -c "from utils import EnvironmentValidator; print(EnvironmentValidator.validate_configuration())"

# Interactive demo
python3 examples/quick_demo.py
```

## 🎛️ Advanced Configuration

### Tag-Based Filtering
```env
# Only test user-related endpoints
SPEC_INCLUDE_TAGS=users,accounts

# Exclude dangerous operations
SPEC_EXCLUDE_TAGS=admin,delete,billing

# Combine both
SPEC_INCLUDE_TAGS=public,read
SPEC_EXCLUDE_TAGS=admin,write
```

### Load Testing Tuning
```env
# Conservative (production)
MAX_USERS=10
SPAWN_RATE=1
REQUEST_TIMEOUT=30

# Aggressive (staging)
MAX_USERS=100
SPAWN_RATE=10
REQUEST_TIMEOUT=5

# Endurance testing
MAX_USERS=25
SPAWN_RATE=2
RUN_TIME=2h
```

### Authentication Modes

#### JWT Token
```env
AUTH_MODE=jwt
JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature
```

#### API Key
```env
AUTH_MODE=apikey
API_KEY=your-api-key-here
API_KEY_HEADER=X-API-Key  # or custom header
```

#### Username/Password Login
```env
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=test@example.com
LOGIN_PASS=testpassword
```

#### HTTP Basic Auth
```env
AUTH_MODE=basic
BASIC_USER=username
BASIC_PASS=password
```

#### OAuth Client Credentials
```env
AUTH_MODE=oauth
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_TOKEN_URL=https://auth.example.com/oauth/token
OAUTH_SCOPE=read write  # optional
```

## 🐛 Troubleshooting Guide

### Step 1: Quick Health Check
```bash
python3 scenarios/troubleshoot.py --quick
```

### Step 2: Check Configuration
```bash
# View current config
cat .env

# Validate config
python3 scenarios/troubleshoot.py
```

### Step 3: Test OpenAPI Loading
```bash
# Test spec loading
python3 -c "
from openapi_loader import OpenAPILoader
loader = OpenAPILoader()
spec = loader.load_openapi()
print(f'Loaded {len(spec.get(\"paths\", {}))} paths')
"
```

### Step 4: Test Authentication
```bash
# Test auth setup
python3 -c "
from auth import AuthenticationManager
auth = AuthenticationManager()
headers = auth.get_auth_headers()
print(f'Auth headers: {headers}')
"
```

### Step 5: Test Endpoint Analysis
```bash
# Quick analysis
python3 endpoint_visualizer.py --no-health-check
```

## 📊 Understanding Reports

### Locust Web UI (http://localhost:8089)
- **Charts**: Real-time RPS, response times, user count
- **Statistics**: Per-endpoint metrics
- **Failures**: Error details and rates
- **Download**: CSV data export

### Generated Reports
- `reports/report.html`: Comprehensive test summary
- `reports/results_*.csv`: Raw statistics data
- `reports/endpoint_analysis.json`: API discovery results

### Key Metrics to Watch
- **RPS (Requests Per Second)**: System throughput
- **Response Time P95**: 95% of requests complete within this time
- **Error Rate**: Percentage of failed requests
- **Concurrent Users**: Active load on system

##  CI/CD Integration

### GitHub Actions Example
```yaml
- name: Load Test Staging
  run: |
    docker compose run --rm \
      -e OPENAPI_URL=${{ secrets.STAGING_OPENAPI_URL }} \
      -e BASE_URL=${{ secrets.STAGING_BASE_URL }} \
      -e AUTH_MODE=jwt \
      -e JWT_TOKEN=${{ secrets.STAGING_JWT_TOKEN }} \
      -e MAX_USERS=25 \
      -e SPAWN_RATE=3 \
      -e RUN_TIME=5m \
      locust

- name: Archive Reports
  uses: actions/upload-artifact@v3
  with:
    name: load-test-reports
    path: reports/
```

### GitLab CI Example
```yaml
load_test:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker compose run --rm
        -e OPENAPI_URL=$STAGING_OPENAPI_URL
        -e BASE_URL=$STAGING_BASE_URL
        -e RUN_TIME=3m
        locust
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
```

## 🔄 Development Workflow

### 1. API Development
```bash
# Start with mock server during development
python3 tests/mock_api_server.py &
cp examples/.env.mock_server .env
docker compose up --build
```

### 2. Staging Validation
```bash
# Test staging environment
cp examples/.env.login_flow .env
# Edit with staging credentials
python3 endpoint_visualizer.py  # Analyze first
docker compose up --build       # Then load test
```

### 3. Production Readiness
```bash
# Conservative production testing
cp examples/.env.production_safe .env
# Edit with production values
python3 scenarios/troubleshoot.py  # Validate setup
# Start with very low load
MAX_USERS=1 RUN_TIME=1m docker compose run --rm locust
```

## 💡 Best Practices

### Safety First
- ✅ Always test on staging before production
- ✅ Start with read-only operations
- ✅ Use conservative user counts initially
- ✅ Monitor system resources during tests
- ✅ Have rollback plan ready

### Configuration Management
- ✅ Use example configs as templates
- ✅ Version control your .env files (without secrets)
- ✅ Document your API-specific settings
- ✅ Test configuration validation before running

### Monitoring & Analysis
- ✅ Generate endpoint analysis before testing
- ✅ Monitor error rates and response times
- ✅ Save reports for trend analysis
- ✅ Set up alerts for critical metrics

### Team Collaboration
- ✅ Share configuration templates
- ✅ Document API-specific considerations
- ✅ Establish load testing standards
- ✅ Review results as a team

## 🆘 Getting Help

### Quick Commands
```bash
# Interactive help
python3 quick_start.py

# Quick health check
python3 scenarios/troubleshoot.py --quick

# Full diagnostics
python3 scenarios/troubleshoot.py

# API analysis
python3 endpoint_visualizer.py

# Interactive demo
python3 examples/quick_demo.py
```

### Common Issues Repository
Check `scenarios/troubleshoot.py` for automated diagnosis of:
- Docker configuration issues
- Network connectivity problems
- OpenAPI specification errors
- Authentication failures
- Configuration validation errors

### Resources
- 📖 Framework documentation: `README.md`
- 🔧 Configuration validator: `src/config_validator.py`
- 🐛 Debug utilities: `src/debug_utils.py`
- 📊 Endpoint analyzer: `src/endpoint_visualizer.py`
- 🧪 Test suite: `tests/`
- 🖥️ Mock server: `tests/mock_api_server.py`

---

## 🛠️ Advanced Development Features

### Configuration Validation

The framework includes comprehensive configuration validation:

```bash
# Validate current configuration
make validate

# Or run directly
python3 src/config_validator.py

# Run health check
python3 src/config_validator.py --health
```

**Features:**
- ✅ Environment variable validation
- ✅ URL format checking
- ✅ Authentication configuration validation
- ✅ Safety limit warnings
- ✅ Network connectivity testing
- ✅ OpenAPI spec accessibility checking

### Interactive Debugging

For troubleshooting and development, use the interactive debug utility:

```bash
# Interactive debugging session
python3 src/debug_utils.py --interactive

# Quick debug check
python3 src/debug_utils.py --quick
```

**Debug capabilities:**
- 🔧 Configuration analysis
- 🔐 Authentication testing
- 📋 OpenAPI spec inspection
- 🎯 Scenario generation testing
- 🌐 Network connectivity checking
- 🧪 Single endpoint testing
- 💾 Debug info export

### Development Testing

Run the comprehensive test suite:

```bash
# Run all tests locally
make dev-test

# Run specific test file
python3 -m pytest tests/test_auth.py -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=html
```

### Error Handling and Logging

The framework includes structured error handling:

```python
from src.exceptions import (
    AuthenticationError,
    ConfigurationError,
    OpenAPIError
)
from src.logger import get_logger

logger = get_logger(__name__)

try:
    # Your code here
    pass
except AuthenticationError as e:
    logger.error(f"Authentication failed: {e}")
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
```

**Log levels available:**
- `DEBUG`: Detailed debugging information
- `INFO`: General information messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical error messages

### Custom Extensions

The framework is designed to be extensible:

```python
# Custom authentication method
from src.auth import AuthenticationManager

class CustomAuthManager(AuthenticationManager):
    def get_custom_headers(self):
        # Your custom logic here
        return {"Custom-Header": "value"}

# Custom scenario builder
from src.scenario_builder import ScenarioBuilder

class CustomScenarioBuilder(ScenarioBuilder):
    def build_custom_scenarios(self, spec):
        # Your custom scenario logic
        return custom_scenarios
```

### Package Structure

The `src/` directory is organized as a proper Python package:

```python
# Import framework components
from src import auth, openapi_loader, scenario_builder
from src.logger import get_logger
from src.config_validator import validate_config
from src.debug_utils import quick_debug

# Use in your own code
logger = get_logger(__name__)
auth_manager = auth.AuthenticationManager()
```

### Make Commands Reference

```bash
# Core commands
make help          # Show all available commands
make demo          # Run demo with Swagger Petstore
make test          # Run framework tests
make validate      # Validate configuration
make setup         # Copy example configuration

# Development commands
make dev-test      # Run Python tests locally
make analyze       # Analyze OpenAPI specification
make mock          # Start local mock API server
make health        # Run health check
make build         # Build Docker images
make clean         # Clean up everything
make logs          # Show container logs
```

---

*🎯 This framework is designed to be production-ready while maintaining developer-friendly features for testing, debugging, and extension.*