# Dynamic Stress Tests - Automatic Load Testing from OpenAPI

<p align="center">
     <a href="https://locust.io/" target="_blank" rel="noopener noreferrer">
          <img src="https://img.shields.io/badge/Built%20with-Locust-43B02A?logo=locust&logoColor=white" alt="Locust" />
     </a>
     <a href="https://swagger.io/specification/" target="_blank" rel="noopener noreferrer">
          <img src="https://img.shields.io/badge/OpenAPI-3.0-85EA2D?logo=openapiinitiative&logoColor=white" alt="OpenAPI 3.0" />
     </a>
</p>

**Automatically generate comprehensive load tests from your OpenAPI/Swagger specification.**

Transform your API documentation into production-ready load tests in minutes. This tool reads your OpenAPI spec and creates realistic test scenarios for every endpoint, including automatic authentication for protected routes.

## What It Does

🎯 **Automatic Test Generation**: Scans your OpenAPI spec and creates load tests for all endpoints
🔐 **Smart Authentication**: Automatically handles JWT, API keys, OAuth, and login flows
📊 **Real-time Monitoring**: Live dashboard with performance metrics and insights
🛡️ **Production Safe**: Built-in safety controls and gradual scaling
🐳 **Docker Ready**: Complete containerization with zero setup complexity

## How Automatic Authentication Works

The framework intelligently handles authentication for protected endpoints by:

### 1. **Authentication Detection**
```bash
OpenAPI Spec Analysis → Security Schemes Detection → Endpoint Protection Mapping
```

### 2. **Automatic Token Generation**
Based on your `.env` configuration, the tool:
- **JWT**: Uses provided token directly or refreshes it automatically
- **API Key**: Injects key into headers/query parameters as specified
- **OAuth**: Handles token exchange and refresh flows
- **Login Flow**: Performs login request and extracts session/token

### 3. **Smart Request Enhancement**
```bash
Endpoint Request → Authentication Check → Token Injection → Load Test Execution
```

### Example Authentication Flow
```env
# Your .env configuration
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=test@example.com
LOGIN_PASS=password
BASE_URL=https://your-api.com
OPENAPI_URL=https://your-api.com/swagger.json
```

**What happens automatically:**
1. Tool reads OpenAPI spec from `OPENAPI_URL`
2. Identifies protected endpoints (those with security requirements)
3. Performs login at `LOGIN_URL` with credentials
4. Extracts authentication token from response
5. Applies token to all subsequent requests to protected endpoints
6. Generates load tests for ALL endpoints (protected + public)

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

## Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- OpenAPI/Swagger specification URL

### Simple 3-Step Setup
```bash
make setup
# Edit .env with your API details
make validate
make demo
```

Open http://localhost:8089 to access the real-time testing dashboard.

### Example Configuration
```env
# Basic API configuration
OPENAPI_URL=https://your-api.com/openapi.json
BASE_URL=https://your-api.com
MAX_USERS=10
SPAWN_RATE=2

# Authentication (choose one method)
AUTH_MODE=none                    # For public APIs
# AUTH_MODE=jwt                   # For JWT token auth
# AUTH_MODE=apikey               # For API key auth
# AUTH_MODE=login                # For username/password login
```

## Documentation

### English Documentation
- **[Command Reference](doc/COMMANDS.md)** - Detailed command documentation with procedures and testing flows
- **[API Testing Guide](doc/API_TESTING.md)** - Complete testing methodology and dynamic test generation
- **[CI/CD Integration](doc/CICD.md)** - Production deployment with AWS Fargate examples
- **[Parameters Reference](doc/PARAMETERS.md)** - Complete configuration guide
- **[Developer Guide](doc/DEVELOPER_GUIDE.md)** - Advanced development features

### Documentação em Português (Brasil)
- **[Referência de Comandos](doc/pt-br/COMMANDS_pt-BR.md)** - Documentação detalhada de comandos
- **[Guia de Testes de API](doc/pt-br/API_TESTING_pt-BR.md)** - Metodologia completa de testes
- **[Integração CI/CD](doc/pt-br/CICD_pt-BR.md)** - Deploy em produção com exemplos AWS Fargate
- **[Referência de Parâmetros](doc/pt-br/PARAMETERS_pt-BR.md)** - Guia completo de configuração
- **[Guia do Desenvolvedor](doc/pt-br/DEVELOPER_GUIDE_pt-BR.md)** - Recursos avançados de desenvolvimento

## Authentication Examples

## Authentication Examples

### JWT Token Authentication
```env
AUTH_MODE=jwt
JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key Authentication
```env
AUTH_MODE=apikey
API_KEY=your-secret-api-key-here
API_KEY_HEADER=X-API-Key  # Optional: custom header name
```

### Username/Password Login Flow
```env
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=test@example.com
LOGIN_PASS=your-password
```

## Key Features

- **🔄 Auto-generates tests** from OpenAPI/Swagger specifications
- **🔐 Smart authentication** for JWT, API keys, OAuth, and login flows
- **🛡️ Production-safe defaults** with comprehensive validation
- **📊 Real-time monitoring** with web-based dashboard
- **🐛 Interactive debugging** and troubleshooting tools
- **📈 Extensive test coverage** with automated scenario generation
- **🐳 Container-ready** with complete Docker orchestration
- **⚙️ CI/CD integration** with detailed reporting

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
