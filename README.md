# Dynamic Stress Tests

Automated load testing framework that generates comprehensive tests from OpenAPI specifications.

## Quick Start

```bash
git clone <repository-url>
cd dynamic-stress-tests
make demo
```

Open http://localhost:8089 to access the Locust web interface.

## Commands

| Command | Description |
|---------|-------------|
| `make demo` | Quick demo (Swagger Petstore) |
| `make test` | Run framework tests |
| `make setup` | Copy example config |
| `make clean` | Clean up everything |
| `make mock` | Start local mock server |
| `make health` | Check system health |

## Testing Your API

1. **Setup**:
   ```bash
   make setup
   ```

2. **Edit configuration**:
   ```bash
   # Edit .env with your API details
   nano .env
   ```

3. **Run test**:
   ```bash
   make demo
   ```

4. **View results**:
   - Web UI: http://localhost:8089
   - Reports: `reports/report.html`

## Configuration

### Basic Configuration
```env
OPENAPI_URL=https://your-api.com/openapi.json
BASE_URL=https://your-api.com
AUTH_MODE=none
MAX_USERS=10
SPAWN_RATE=2
```

### Authentication Examples
```env
# JWT Token
AUTH_MODE=jwt
JWT_TOKEN=your.jwt.token.here

# API Key
AUTH_MODE=apikey
API_KEY=your-api-key

# Username/Password
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=user@example.com
LOGIN_PASS=password
```

**📖 Complete Parameter Documentation: [doc/PARAMETERS.md](doc/PARAMETERS.md)**

All parameters are fully documented with examples, validation rules, and security considerations.

## Test Scenarios

### Spike Testing
Sudden traffic surge simulation:
```bash
make spike
```

### Endurance Testing
Long-duration stability testing:
```bash
make soak
```

### Local Development
Test against local mock server:
```bash
make mock          # Terminal 1: Start mock API
make config-mock   # Terminal 2: Configure
make demo          # Terminal 2: Run tests
```

## Reports and Analysis

The framework generates multiple types of reports:

### Web Interface
Real-time statistics available at http://localhost:8089:
- Request rates and response times
- Error rates and failure details
- User load patterns

### Generated Reports
- `reports/report.html` - Comprehensive test summary
- `reports/endpoint_analysis.json` - API discovery results
- `reports/results_*.csv` - Raw performance data

### Endpoint Analysis
Before running load tests, analyze your API:
```bash
make analyze
```

This generates:
- Endpoint discovery summary
- Complexity analysis
- Authentication requirements
- HTML report with visualizations

## Framework Features

### Automatic Test Generation
- Parses OpenAPI specifications automatically
- Generates realistic request payloads
- Handles path parameters and query strings
- Supports all HTTP methods (GET, POST, PUT, DELETE, etc.)

### Authentication Support
- JWT tokens
- API keys
- Username/password login flows
- OAuth client credentials
- HTTP Basic authentication

### Smart Filtering
Control which endpoints to test:
```env
SPEC_INCLUDE_TAGS=users,orders    # Only test these categories
SPEC_EXCLUDE_TAGS=admin,delete    # Skip these operations
```

### Safety Features
- Production-safe configurations
- Conservative default settings
- Read-only operation filtering
- Rate limiting controls

## Development

### Local Setup
```bash
make dev-setup     # Install Python dependencies
make test-local    # Run tests without Docker
```

### Mock API Server
For development and testing:
```bash
make mock          # Starts server at http://localhost:5000
```

The mock server provides:
- RESTful API with users and posts
- Authentication testing endpoints
- Realistic response times
- Error simulation

## Troubleshooting

### Quick Health Check
```bash
make health
```

### Common Issues

**Docker not running**:
```bash
# Check Docker status
docker --version
docker info
```

**Configuration errors**:
```bash
# Validate your .env file
make health
```

**OpenAPI spec issues**:
```bash
# Test spec loading
make analyze
```

**Authentication problems**:
```bash
# Test auth configuration
make health
```

## Production Usage

### Safety Guidelines
1. Always test on staging first
2. Start with very low user counts
3. Monitor system resources during tests
4. Use read-only operations initially
5. Have rollback procedures ready

### Production Configuration
```bash
make safe          # Copy production-safe template
# Edit .env with production values
# Start with MAX_USERS=1, increase gradually
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Load Test Staging
  run: |
    docker compose run --rm \
      -e OPENAPI_URL=${{ secrets.STAGING_OPENAPI_URL }} \
      -e BASE_URL=${{ secrets.STAGING_BASE_URL }} \
      -e MAX_USERS=25 \
      -e RUN_TIME=5m \
      locust

- name: Archive Reports
  uses: actions/upload-artifact@v3
  with:
    name: load-test-reports
    path: reports/
```

### Docker Compose
For CI environments:
```bash
# Headless execution with time limit
RUN_TIME=10m MAX_USERS=50 docker compose run --rm locust
```

## Architecture

The framework consists of several key components:

- **OpenAPI Loader**: Fetches and validates API specifications
- **Scenario Builder**: Generates test scenarios from specifications
- **Authentication Manager**: Handles various auth methods
- **Locust Integration**: Executes load tests and collects metrics
- **Report Generator**: Creates comprehensive test reports

## Advanced Features

### Tag-Based Testing
Focus on specific API areas:
```env
SPEC_INCLUDE_TAGS=public,core      # Test only core public endpoints
SPEC_EXCLUDE_TAGS=admin,beta       # Skip admin and beta features
```

### Custom Headers
Add environment-specific headers:
```env
EXTRA_HEADERS={"X-Environment":"staging","X-Test-Run":"load-test"}
```

### Retry Logic
Configure resilience testing:
```env
REQUEST_TIMEOUT=15    # Seconds per request
RETRY_COUNT=3         # Retry failed requests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**Built for reliable API load testing and performance validation.**