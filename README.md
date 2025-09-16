# Dynamic Stress Tests

🚀 **Production-ready automated load testing framework** that generates comprehensive tests from OpenAPI specifications with built-in safety features, validation, and debugging tools.

## ✨ Key Features

- 🔄 **Auto-generates tests** from OpenAPI/Swagger specs
- 🔐 **Multiple authentication methods** (JWT, API keys, OAuth, Basic Auth)
- 🛡️ **Production-safe defaults** and validation
- 📊 **Comprehensive reporting** with real-time web UI
- 🐛 **Interactive debugging** and troubleshooting tools
- 🧪 **Extensive test suite** with pytest integration
- 🐳 **Docker-ready** with docker-compose orchestration
- 📖 **Complete documentation** and developer guides

## 🚀 Quick Start

```bash
git clone <repository-url>
cd dynamic-stress-tests
make demo
```

Open http://localhost:8089 to access the Locust web interface.

## 📋 Commands

| Command | Description |
|---------|-------------|
| `make demo` | Quick demo (Swagger Petstore) |
| `make validate` | Validate configuration |
| `make test` | Run framework tests |
| `make setup` | Copy example config |
| `make health` | Run health check |
| `make analyze` | Analyze OpenAPI spec |
| `make mock` | Start local mock server |
| `make dev-test` | Run Python tests locally |
| `make clean` | Clean up everything |

## 🎯 Testing Your API

### 1. **Setup & Validation**
```bash
make setup              # Copy example configuration
nano .env              # Edit with your API details
make validate          # Validate configuration
```

### 2. **Run Load Tests**
```bash
make demo              # Start load testing
```

### 3. **View Results**
- **Web UI**: http://localhost:8089 (real-time metrics)
- **Reports**: `reports/report.html` (detailed analysis)
- **Debug**: `python3 src/debug_utils.py` (troubleshooting)

### 4. **Health Monitoring**
```bash
make health           # System health check
make analyze          # OpenAPI analysis
```

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

## 🏗️ Architecture

### Core Components
```
src/
├── locustfile.py           # Main Locust test execution
├── openapi_loader.py       # OpenAPI specification loading
├── scenario_builder.py     # Test scenario generation
├── auth.py                 # Authentication management
├── config_validator.py     # Configuration validation
├── logger.py               # Structured logging
├── debug_utils.py          # Interactive debugging
├── exceptions.py           # Custom error handling
└── utils.py                # Utility functions
```

### Enhanced Framework Features

#### 🔍 **Configuration Validation**
```bash
make validate              # Comprehensive config validation
python3 src/config_validator.py --health  # Health check
```
- ✅ Environment variable validation
- ✅ URL format checking
- ✅ Authentication setup verification
- ✅ Network connectivity testing
- ✅ Safety limit warnings

#### 🐛 **Interactive Debugging**
```bash
python3 src/debug_utils.py --interactive  # Full debug session
python3 src/debug_utils.py --quick        # Quick health check
```
- 🔧 Configuration analysis
- 🔐 Authentication testing
- 📋 OpenAPI spec inspection
- 🎯 Single endpoint testing
- 💾 Debug info export

#### 🧪 **Comprehensive Testing**
```bash
make dev-test             # Run Python test suite
python3 -m pytest tests/ -v --cov=src    # With coverage
```
- ✅ Unit tests for all components
- ✅ Integration tests
- ✅ Configuration validation tests
- ✅ Authentication method tests
- ✅ Pytest fixtures and mocks

#### 📝 **Structured Logging**
- Environment-aware log levels
- Structured error handling
- Debug, info, warning, error, and critical levels
- File and console output options
- Production-safe logging configurations

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

## 📚 Documentation

- 📖 **[Parameter Guide](doc/PARAMETERS.md)** - Complete parameter documentation
- 🛠️ **[Developer Guide](doc/DEVELOPER_GUIDE.md)** - Advanced development features
- 📋 **[Project Requirements](doc/CLAUDE.md)** - Project blueprint and requirements

## 🚀 Development Workflow

### Local Development
```bash
# Setup development environment
make setup
make validate          # Ensure config is valid

# Interactive debugging
python3 src/debug_utils.py --interactive

# Run test suite
make dev-test

# Analyze your API
make analyze
```

### Testing Workflow
```bash
# 1. Start with validation
make validate

# 2. Analyze API structure
make analyze

# 3. Test with low load
MAX_USERS=5 SPAWN_RATE=1 make demo

# 4. Scale up gradually
MAX_USERS=25 SPAWN_RATE=3 make demo
```

### Production Deployment
```bash
# Use conservative settings
cp examples/.env.production_safe .env
# Edit with production values
make validate          # Validate before deployment
make health           # Health check
```

## 🆘 Troubleshooting

### Quick Diagnostics
```bash
make health           # System health check
make validate         # Configuration validation
python3 src/debug_utils.py --quick  # Quick debug
```

### Interactive Debugging
```bash
python3 src/debug_utils.py --interactive
# Menu-driven debugging session with:
# - Configuration analysis
# - Authentication testing
# - OpenAPI spec inspection
# - Network connectivity testing
# - Single endpoint testing
```

### Common Issues
- **Config errors**: Run `make validate`
- **Auth failures**: Use debug tools to test auth setup
- **Network issues**: Check `make health` for connectivity
- **No scenarios**: Review tag filters and OpenAPI spec

## 📊 Monitoring & Reports

### Real-time Monitoring
- **Web UI**: http://localhost:8089
- **Live metrics**: RPS, response times, error rates
- **User simulation**: Concurrent user management

### Generated Reports
- `reports/report.html` - Comprehensive test summary
- `reports/results_*.csv` - Raw performance data
- `reports/endpoint_analysis.json` - API structure analysis
- `reports/debug_info_*.json` - Debug session exports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make dev-test`
5. Validate: `make validate`
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**🎯 Production-ready load testing framework designed for safety, reliability, and developer productivity.**