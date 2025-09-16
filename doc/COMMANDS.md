# Command Reference

This guide provides detailed documentation for all available commands, their procedures, testing scenarios, and execution order for optimal results.

## Command Overview

The framework provides a step-by-step workflow designed for safe and effective load testing. Commands are organized by purpose and should be executed in the recommended order for best results.

## Setup and Validation Commands

### `make setup`

**Purpose**: Initialize configuration for your API testing
**Procedure**:
- Copies example configuration template to `.env`
- Creates base configuration for immediate use
- Provides template for API-specific customization

**What it emulates**: Initial project setup and configuration preparation
**Usage**: Always run first before any testing

```bash
make setup
```

**Next steps**: Edit `.env` file with your API details, then run `make validate`

### `make validate`

**Purpose**: Comprehensive configuration validation and safety checks
**Procedure**:
- Validates environment variables and format
- Tests network connectivity to API endpoints
- Verifies authentication configuration
- Checks OpenAPI specification accessibility
- Validates safety limits and parameters

**What it emulates**: Pre-flight safety checks before testing
**RPS Impact**: No load testing - validation only
**User Load**: N/A - configuration testing only

```bash
make validate
```

**Scenarios covered**:
- Configuration syntax validation
- Network connectivity testing
- Authentication method verification
- OpenAPI specification parsing
- Safety parameter validation

### `make health`

**Purpose**: Quick system health check and connectivity test
**Procedure**:
- Tests basic system components
- Verifies Docker and network connectivity
- Checks API endpoint accessibility
- Validates minimal configuration requirements

**What it emulates**: System readiness check
**Usage**: Troubleshooting and pre-test verification

```bash
make health
```

## Analysis Commands

### `make analyze`

**Purpose**: Comprehensive OpenAPI specification analysis and endpoint discovery
**Procedure**:
- Parses OpenAPI/Swagger specification
- Discovers all available endpoints
- Analyzes authentication requirements
- Identifies test complexity levels
- Generates endpoint visualization reports

**What it emulates**: API exploration and test planning phase
**Output**: HTML reports in `reports/` directory with endpoint analysis

```bash
make analyze
```

**Scenarios covered**:
- Endpoint discovery and categorization
- Authentication requirement analysis
- Parameter complexity assessment
- Test scenario identification

## Testing Commands (Execution Order)

### Step 1: `make demo`

**Purpose**: Primary load testing execution with real-time monitoring
**Procedure**:
- Builds Docker containers with test framework
- Parses OpenAPI specification for test generation
- Initializes authentication if configured
- Starts Locust load testing with web interface
- Generates real-time performance metrics

**What it emulates**: Realistic user behavior based on API specification
**Default RPS**: Gradually increases from 0 to MAX_USERS/SPAWN_RATE
**Default User Load**: 10 concurrent users (configurable via MAX_USERS)
**Spawn Rate**: 2 users per second (configurable via SPAWN_RATE)

```bash
# Default execution
make demo

# Custom user load and RPS
MAX_USERS=25 SPAWN_RATE=3 make demo

# Production-safe testing
MAX_USERS=5 SPAWN_RATE=1 make demo
```

**Scenarios covered**:
- GET requests for data retrieval
- POST requests with realistic payloads
- PUT/PATCH requests for data updates
- DELETE requests (if enabled in configuration)
- Authentication flow testing
- Error handling and retry logic
- Response time measurement
- Concurrent user simulation

**Testing Flow**:
1. Load OpenAPI specification
2. Generate test scenarios for each endpoint
3. Initialize authentication tokens/keys
4. Start with 0 users, gradually increase to MAX_USERS
5. Maintain steady load for duration
6. Generate performance reports

### Step 2: `make test`

**Purpose**: Framework validation and comprehensive testing
**Procedure**:
- Runs internal framework tests
- Validates test generation accuracy
- Executes comprehensive test scenarios
- Verifies authentication mechanisms
- Tests error handling and edge cases

**What it emulates**: Framework reliability testing
**Usage**: Verify framework functionality before critical testing

```bash
make test
```

## Development and Mock Testing

### `make mock`

**Purpose**: Local development testing with mock API server
**Procedure**:
- Starts local mock API server on port 5000
- Provides realistic API endpoints for testing
- Simulates authentication flows
- Offers error scenarios for testing

**What it emulates**: Complete API environment for development
**RPS**: Configurable, safe for development
**User Load**: Recommended 5-10 users for development

```bash
make mock
```

**Mock API Features**:
- RESTful endpoints for users and posts
- Authentication testing endpoints
- Realistic response times
- Error simulation capabilities

### `make dev-test`

**Purpose**: Local Python test suite execution
**Procedure**:
- Runs pytest test suite locally
- Tests individual components
- Validates configuration parsing
- Tests authentication methods

**What it emulates**: Unit and integration testing
**Usage**: Development and pre-deployment testing

```bash
make dev-test
```

## Maintenance Commands

### `make clean`

**Purpose**: Complete environment cleanup
**Procedure**:
- Stops all Docker containers
- Removes Docker volumes and images
- Cleans generated reports
- Resets environment to initial state

**Usage**: Reset environment or troubleshoot issues

```bash
make clean
```

## Command Execution Order

### For New API Testing

1. **`make setup`** - Initialize configuration
2. **Edit `.env`** - Configure API details
3. **`make validate`** - Verify configuration
4. **`make analyze`** - Understand API structure
5. **`make demo`** - Start with low user load
6. **Scale gradually** - Increase MAX_USERS progressively

### For Development

1. **`make setup`** - Initialize configuration
2. **`make mock`** - Start mock API server
3. **`make dev-test`** - Run test suite
4. **`make demo`** - Test against mock API

### For Production Testing

1. **`make validate`** - Comprehensive validation
2. **`make analyze`** - API analysis
3. **`make demo`** (MAX_USERS=1) - Single user test
4. **Scale gradually** - Increase load incrementally
5. **Monitor continuously** - Watch real-time metrics

## Performance Parameters

### User Load Scaling

```bash
# Development testing
MAX_USERS=5 SPAWN_RATE=1 make demo

# Staging environment
MAX_USERS=25 SPAWN_RATE=3 make demo

# Production testing (start conservative)
MAX_USERS=50 SPAWN_RATE=5 make demo
```

### RPS (Requests Per Second) Calculation

RPS depends on:
- Number of concurrent users (MAX_USERS)
- Number of endpoints being tested
- Response times of your API
- Think time between requests

**Estimated RPS**: MAX_USERS × (Number of endpoints / Average response time)

### Load Testing Scenarios

The framework automatically covers:

1. **Baseline Testing**: Single user, single endpoint
2. **Load Testing**: Normal expected traffic
3. **Stress Testing**: Above normal capacity
4. **Spike Testing**: Sudden traffic increases
5. **Endurance Testing**: Extended duration testing

## Monitoring and Reports

### Real-time Monitoring

Access web interface at `http://localhost:8089` during testing:
- Live RPS metrics
- Response time distributions
- Error rates and failure details
- User load patterns
- Request/response statistics

### Generated Reports

After testing completion:
- `reports/report.html` - Comprehensive test summary
- `reports/endpoint_analysis.json` - API structure analysis
- `reports/results_*.csv` - Raw performance data
- `reports/debug_info_*.json` - Debug session exports

## Troubleshooting Commands

### Quick Diagnostics

```bash
make health           # System health check
make validate         # Configuration validation
make analyze          # API specification test
```

### Debug Mode

```bash
# Interactive debugging session
python3 src/debug_utils.py --interactive

# Quick debug check
python3 src/debug_utils.py --quick
```

## Safety Guidelines

1. **Always start with low user counts** (MAX_USERS=1-5)
2. **Validate configuration** before testing
3. **Monitor system resources** during tests
4. **Use staging environments** before production
5. **Increase load gradually** to identify limits
6. **Have rollback procedures** ready for production tests

## Advanced Configuration

### Environment Variables for Commands

```bash
# Customize test duration
RUN_TIME=10m make demo

# Override user limits
MAX_USERS=100 SPAWN_RATE=10 make demo

# Enable specific tags
SPEC_INCLUDE_TAGS=users,orders make demo

# Exclude dangerous operations
SPEC_EXCLUDE_TAGS=admin,delete make demo
```

This command reference ensures safe, effective, and comprehensive API load testing with clear understanding of each step's purpose and impact.