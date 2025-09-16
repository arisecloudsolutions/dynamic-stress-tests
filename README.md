# Dynamic Stress Tests - Automated Load Testing from OpenAPI Specs and Locust
<p align="center">
     <a href="https://locust.io/" target="_blank" rel="noopener noreferrer">
          <img src="https://img.shields.io/badge/Built%20with-Locust-43B02A?logo=locust&logoColor=white" alt="Locust" />
     </a>
</p>


Production-ready automated load testing framework that generates comprehensive tests from OpenAPI specifications with built-in safety features, validation, and debugging tools.

## Core Concept

This framework bridges the gap between API documentation and testing reality. By parsing OpenAPI specifications, it automatically creates realistic load tests that evolve with your API documentation. The key principle is maintaining synchronized testing with your API changes - when your OpenAPI spec updates, your tests automatically adapt.

The framework emphasizes safety and gradual scaling, making it suitable for testing production environments with confidence. It provides comprehensive insights into API behavior under load while maintaining strict safety controls.

## Architecture Overview

```
OpenAPI Spec → Auto-Generated Tests → Load Testing → Real-time Analysis
     ↓              ↓                    ↓              ↓
Documentation    Realistic            Performance    Actionable
Synchronization  Scenarios            Metrics        Insights
```

## Key Features

- **Auto-generates tests** from OpenAPI/Swagger specifications
- **Multiple authentication methods** (JWT, API keys, OAuth, Basic Auth)
- **Production-safe defaults** with comprehensive validation
- **Real-time monitoring** with web-based dashboard
- **Interactive debugging** and troubleshooting tools
- **Extensive test coverage** with automated scenario generation
- **Container-ready** with complete Docker orchestration
- **CI/CD integration** with detailed reporting

## Quick Start

```bash
make setup
# Edit .env with your API details
make validate
make demo
```

Open http://localhost:8089 to access the real-time testing dashboard.

## Documentation

- **[Command Reference](doc/COMMANDS.md)** - Detailed command documentation with procedures and testing flows
- **[API Testing Guide](doc/API_TESTING.md)** - Complete testing methodology and dynamic test generation
- **[CI/CD Integration](doc/CICD.md)** - Production deployment with AWS Fargate examples
- **[Parameters Reference](doc/PARAMETERS.md)** - Complete configuration guide
- **[Developer Guide](doc/DEVELOPER_GUIDE.md)** - Advanced development features

## Configuration

Basic setup requires minimal configuration:

```env
OPENAPI_URL=https://your-api.com/openapi.json
BASE_URL=https://your-api.com
AUTH_MODE=none
MAX_USERS=10
SPAWN_RATE=2
```

Authentication examples:
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

## Safety Features

The framework prioritizes safe testing practices:

- Conservative default settings for production environments
- Comprehensive validation before test execution
- Rate limiting and resource protection
- Read-only operation filtering
- Gradual load scaling recommendations
- Real-time monitoring with automatic alerts

## Production Usage

For production environments, the framework provides:

1. **Staging Environment Validation** - Comprehensive pre-production testing
2. **Gradual Load Scaling** - Step-by-step user load increases
3. **Real-time Monitoring** - Live performance metrics and alerts
4. **Safety Controls** - Automatic protection against dangerous configurations
5. **Comprehensive Reporting** - Detailed analysis for performance optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run validation: `make validate`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## References

- [OpenAPI Specification](https://swagger.io/specification/) - Official documentation for OpenAPI standards used by this framework
- [Locust Documentation](https://docs.locust.io/) - Core load testing engine documentation

---

**Production-ready load testing framework designed for safety, reliability, and developer productivity.**