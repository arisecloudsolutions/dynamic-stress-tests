# Configuration Parameters

Complete reference for all configuration parameters used in the Dynamic Stress Testing Framework.

## Required Parameters

### OpenAPI Source
**One of these is required:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `OPENAPI_URL` | URL | HTTP(S) URL to OpenAPI specification | `https://api.example.com/openapi.json` |
| `OPENAPI_PATH` | Path | Local file path to OpenAPI specification | `/app/specs/openapi.json` |

### Target API

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `BASE_URL` | URL | Base URL of the API to test | `https://api.example.com` |

## Authentication Parameters

### No Authentication
```env
AUTH_MODE=none
```

### JWT Token Authentication
```env
AUTH_MODE=jwt
JWT_TOKEN=your.jwt.token.here
```

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `JWT_TOKEN` | String | Yes | Bearer token for authentication | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### API Key Authentication
```env
AUTH_MODE=apikey
API_KEY=your-api-key
API_KEY_HEADER=X-API-Key
```

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `API_KEY` | String | Yes | API key value | `abc123xyz789` |
| `API_KEY_HEADER` | String | No | Header name for API key | `X-API-Key` (default) |

### Username/Password Login
```env
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=username
LOGIN_PASS=password
```

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `LOGIN_URL` | String | Yes | Login endpoint path or full URL | `/auth/login` |
| `LOGIN_USER` | String | Yes | Username or email | `user@example.com` |
| `LOGIN_PASS` | String | Yes | Password | `mypassword123` |

### HTTP Basic Authentication
```env
AUTH_MODE=basic
BASIC_USER=username
BASIC_PASS=password
```

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `BASIC_USER` | String | Yes | Basic auth username | `apiuser` |
| `BASIC_PASS` | String | Yes | Basic auth password | `apipass` |

### OAuth Client Credentials
```env
AUTH_MODE=oauth
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_TOKEN_URL=https://auth.example.com/token
OAUTH_SCOPE=read write
```

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `OAUTH_CLIENT_ID` | String | Yes | OAuth client identifier | `my-client-id` |
| `OAUTH_CLIENT_SECRET` | String | Yes | OAuth client secret | `my-client-secret` |
| `OAUTH_TOKEN_URL` | URL | Yes | OAuth token endpoint | `https://auth.example.com/oauth/token` |
| `OAUTH_SCOPE` | String | No | OAuth scope (space-separated) | `read write admin` |

## Load Testing Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `MAX_USERS` | Integer | `100` | Maximum concurrent users | `50` |
| `SPAWN_RATE` | Number | `5` | Users spawned per second | `2.5` |
| `RUN_TIME` | Duration | None | Test duration (headless mode only) | `10m`, `2h`, `30s` |
| `REQUEST_TIMEOUT` | Integer | `10` | Request timeout in seconds | `15` |
| `RETRY_COUNT` | Integer | `1` | Number of retries for failed requests | `3` |

### Duration Format
For `RUN_TIME` parameter:
- Seconds: `30s`, `45s`
- Minutes: `5m`, `10m`, `30m`
- Hours: `1h`, `2h`
- Combined: `1h30m`, `2h15m30s`

### Valid Ranges
| Parameter | Minimum | Maximum | Recommended |
|-----------|---------|---------|-------------|
| `MAX_USERS` | 1 | 10000 | 10-100 |
| `SPAWN_RATE` | 0.1 | 1000 | 1-10 |
| `REQUEST_TIMEOUT` | 1 | 300 | 10-30 |
| `RETRY_COUNT` | 0 | 10 | 1-3 |

## Filtering Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `SPEC_INCLUDE_TAGS` | String | Comma-separated tags to include | `users,orders,public` |
| `SPEC_EXCLUDE_TAGS` | String | Comma-separated tags to exclude | `admin,delete,billing` |

### Tag Filtering Examples
```env
# Only test user-related endpoints
SPEC_INCLUDE_TAGS=users,accounts

# Skip dangerous operations
SPEC_EXCLUDE_TAGS=admin,delete,write

# Test only read operations
SPEC_INCLUDE_TAGS=read,get,list
SPEC_EXCLUDE_TAGS=post,put,patch,delete

# Skip admin endpoints but test everything else
SPEC_EXCLUDE_TAGS=admin
```

## Report Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `REPORTS_DIR` | Path | `/mnt/locust/reports` | Directory for generated reports | `/app/reports` |

## Advanced Parameters

### Custom Headers
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `EXTRA_HEADERS` | JSON | Additional HTTP headers | `{"X-Environment":"staging","X-Client":"test"}` |

### Logging
| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `LOG_LEVEL` | String | `INFO` | Python logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Environment-Specific Examples

### Development Environment
```env
OPENAPI_URL=http://localhost:3000/openapi.json
BASE_URL=http://localhost:3000
AUTH_MODE=none
MAX_USERS=5
SPAWN_RATE=1
REQUEST_TIMEOUT=30
LOG_LEVEL=DEBUG
```

### Staging Environment
```env
OPENAPI_URL=https://staging-api.example.com/openapi.json
BASE_URL=https://staging-api.example.com
AUTH_MODE=jwt
JWT_TOKEN=${STAGING_JWT_TOKEN}
MAX_USERS=25
SPAWN_RATE=3
REQUEST_TIMEOUT=15
RETRY_COUNT=2
SPEC_EXCLUDE_TAGS=admin,delete
EXTRA_HEADERS={"X-Environment":"staging"}
```

### Production Environment
```env
OPENAPI_URL=https://api.example.com/openapi.json
BASE_URL=https://api.example.com
AUTH_MODE=apikey
API_KEY=${PRODUCTION_API_KEY}
MAX_USERS=10
SPAWN_RATE=1
REQUEST_TIMEOUT=30
RETRY_COUNT=1
SPEC_INCLUDE_TAGS=public,read
SPEC_EXCLUDE_TAGS=admin,write,delete,post,put,patch
EXTRA_HEADERS={"X-Environment":"production","X-Test-Type":"health-check"}
```

## Parameter Validation

The framework validates all parameters before starting tests:

### Required Parameter Checks
- At least one of `OPENAPI_URL` or `OPENAPI_PATH` must be set
- `BASE_URL` must be a valid HTTP(S) URL
- Authentication parameters must be complete for the chosen `AUTH_MODE`

### Range Validation
- Numeric parameters are checked against valid ranges
- Duration strings are parsed and validated
- URLs are validated for correct format

### Error Messages
When validation fails, the framework provides specific error messages:

```
❌ Configuration Error: Either OPENAPI_URL or OPENAPI_PATH must be provided
❌ AUTH_MODE=jwt requires JWT_TOKEN environment variable
❌ MAX_USERS=abc is not a valid number
❌ BASE_URL must start with http:// or https://
```

## Parameter Precedence

When the same parameter is specified in multiple ways:

1. **Environment variables** (highest priority)
2. **`.env` file**
3. **Default values** (lowest priority)

Example:
```bash
# .env file has MAX_USERS=50
# Command line overrides it
MAX_USERS=100 make demo
```

## Security Considerations

### Sensitive Parameters
These parameters contain sensitive information and should be protected:
- `JWT_TOKEN`
- `API_KEY`
- `LOGIN_PASS`
- `OAUTH_CLIENT_SECRET`

### Best Practices
1. **Use environment variables** for sensitive values in CI/CD
2. **Never commit** `.env` files with real credentials
3. **Use secrets management** in production environments
4. **Rotate tokens regularly**

### CI/CD Example
```yaml
env:
  OPENAPI_URL: https://staging-api.example.com/openapi.json
  BASE_URL: https://staging-api.example.com
  AUTH_MODE: jwt
  JWT_TOKEN: ${{ secrets.STAGING_JWT_TOKEN }}
  MAX_USERS: 25
  SPAWN_RATE: 3
```

## Common Parameter Combinations

### Quick Demo
```env
OPENAPI_URL=https://petstore3.swagger.io/api/v3/openapi.json
BASE_URL=https://petstore3.swagger.io/api/v3
AUTH_MODE=none
MAX_USERS=10
SPAWN_RATE=2
```

### API with Authentication
```env
OPENAPI_URL=https://api.example.com/openapi.json
BASE_URL=https://api.example.com
AUTH_MODE=jwt
JWT_TOKEN=your.token.here
MAX_USERS=50
SPAWN_RATE=5
SPEC_EXCLUDE_TAGS=admin
```

### Production Health Check
```env
OPENAPI_URL=https://api.example.com/openapi.json
BASE_URL=https://api.example.com
AUTH_MODE=apikey
API_KEY=your-api-key
MAX_USERS=5
SPAWN_RATE=1
RUN_TIME=1m
SPEC_INCLUDE_TAGS=health,status,ping
REQUEST_TIMEOUT=30
```

### Load Testing
```env
OPENAPI_URL=https://staging-api.example.com/openapi.json
BASE_URL=https://staging-api.example.com
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=loadtest@example.com
LOGIN_PASS=loadtestpass
MAX_USERS=100
SPAWN_RATE=10
RUN_TIME=10m
SPEC_EXCLUDE_TAGS=admin,delete
REQUEST_TIMEOUT=15
RETRY_COUNT=3
```

## Troubleshooting Parameters

### Common Issues

**"No test scenarios generated"**
```env
# Remove restrictive filters
SPEC_INCLUDE_TAGS=
SPEC_EXCLUDE_TAGS=
```

**"Request timeouts"**
```env
# Increase timeout and retries
REQUEST_TIMEOUT=30
RETRY_COUNT=3
```

**"Too many concurrent users"**
```env
# Reduce load
MAX_USERS=10
SPAWN_RATE=1
```

**"Authentication failed"**
```env
# Check auth parameters
AUTH_MODE=none  # Temporary disable
```

### Parameter Testing
Use the health check to validate parameters:
```bash
make health
```

This command validates all parameters and reports any issues before starting tests.