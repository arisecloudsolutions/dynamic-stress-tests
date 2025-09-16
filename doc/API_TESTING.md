# API Testing Guide

This guide explains the complete testing methodology, dynamic test generation process, and authentication flows used by the framework.

## Testing Philosophy

The framework operates on the principle of **Documentation-Driven Testing**: your OpenAPI specification becomes the single source of truth for load testing. This ensures that tests remain synchronized with your API evolution and provides realistic testing scenarios based on actual API capabilities.

## What Kind of Tests This Framework Performs

### 1. **Functional Load Testing**
- **Purpose**: Verify API functionality under concurrent user load
- **Scope**: All endpoints defined in OpenAPI specification
- **Method**: Realistic request patterns with authentic payloads
- **Validation**: Response codes, payload structure, and performance metrics

### 2. **Authentication Flow Testing**
- **Purpose**: Validate authentication mechanisms under load
- **Scope**: Token acquisition, refresh, and usage patterns
- **Method**: Simulates real user authentication workflows
- **Validation**: Authentication success rates and token management

### 3. **Endurance Testing**
- **Purpose**: Long-duration stability testing
- **Scope**: Extended operation periods with sustained load
- **Method**: Continuous request patterns over extended timeframes
- **Validation**: Memory leaks, connection handling, and performance degradation

### 4. **Stress Testing**
- **Purpose**: Identify breaking points and capacity limits
- **Scope**: Gradual load increase until failure points
- **Method**: Progressive user load scaling
- **Validation**: Failure thresholds and graceful degradation

### 5. **Spike Testing**
- **Purpose**: Sudden traffic surge simulation
- **Scope**: Rapid user count increases
- **Method**: Instant load jumps from baseline to peak
- **Validation**: Recovery patterns and stability under sudden load

## Dynamic Test Generation Process

### Phase 1: OpenAPI Specification Analysis

```
OpenAPI Spec → Parser → Endpoint Discovery → Test Scenario Generation
```

1. **Specification Loading**
   - Downloads and validates OpenAPI/Swagger specification
   - Parses JSON/YAML format with error handling
   - Validates specification completeness and structure

2. **Endpoint Discovery**
   - Extracts all HTTP methods and paths
   - Identifies required vs optional parameters
   - Discovers response schemas and status codes
   - Maps authentication requirements per endpoint

3. **Schema Analysis**
   - Analyzes request/response schemas
   - Identifies data types and validation rules
   - Extracts example values and constraints
   - Maps relationships between endpoints

### Phase 2: Test Scenario Creation

```
Endpoint Data → Payload Generation → Authentication Mapping → Test Scenarios
```

1. **Realistic Payload Generation**
   - Creates valid request bodies from schemas
   - Generates realistic test data following constraints
   - Handles nested objects and array structures
   - Manages required vs optional field combinations

2. **Parameter Handling**
   - Path parameters: Extracted from URL templates
   - Query parameters: Generated from specification
   - Header parameters: Included with authentication
   - Body parameters: Schema-based generation

3. **Authentication Integration**
   - Maps authentication requirements to endpoints
   - Handles multiple authentication schemes
   - Manages token lifecycle and refresh
   - Implements security scheme combinations

### Phase 3: Load Test Execution

```
Test Scenarios → User Simulation → Request Execution → Performance Monitoring
```

1. **User Behavior Simulation**
   - Realistic think times between requests
   - Weighted endpoint selection based on usage patterns
   - Session management and state handling
   - Error handling and retry logic

2. **Concurrent Execution**
   - Scales from 0 to MAX_USERS gradually
   - Maintains steady load for test duration
   - Handles connection pooling and resource management
   - Monitors system resource usage

## Authentication Flow Details

### Token Acquisition Process

The framework handles authentication through multiple methods, each with specific acquisition and management flows:

#### 1. JWT Token Authentication

**Flow**:
```
Configuration → Token Validation → Request Headers → Token Refresh (if needed)
```

**Process**:
1. **Token Validation**: Verifies JWT format and expiration
2. **Header Injection**: Adds Authorization: Bearer {token} to requests
3. **Automatic Refresh**: Handles token renewal when approaching expiration
4. **Error Handling**: Manages authentication failures and retries

**Configuration**:
```env
AUTH_MODE=jwt
JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 2. API Key Authentication

**Flow**:
```
Configuration → Key Validation → Header/Query Injection → Request Execution
```

**Process**:
1. **Key Validation**: Verifies API key format and accessibility
2. **Injection Method**: Adds key to headers or query parameters as specified
3. **Rate Limiting**: Respects API key usage limits
4. **Error Monitoring**: Tracks authentication-related failures

**Configuration**:
```env
AUTH_MODE=apikey
API_KEY=sk-1234567890abcdef
API_KEY_HEADER=X-API-Key  # Optional custom header
```

#### 3. Login Flow Authentication

**Flow**:
```
Login Request → Token Extraction → Session Management → Authenticated Requests
```

**Process**:
1. **Login Execution**: Performs authentication request to login endpoint
2. **Token Extraction**: Extracts JWT/session token from login response
3. **Session Management**: Maintains authentication state across requests
4. **Automatic Re-authentication**: Handles session expiration and renewal

**Configuration**:
```env
AUTH_MODE=login
LOGIN_URL=/auth/login
LOGIN_USER=user@example.com
LOGIN_PASS=secure_password
```

**Dynamic Login Process**:
1. **Pre-test Authentication**: Executes login before starting load tests
2. **Token Caching**: Stores authentication tokens for reuse
3. **Session Monitoring**: Tracks authentication success rates
4. **Failure Recovery**: Re-authenticates on authentication failures

#### 4. OAuth Client Credentials

**Flow**:
```
Client Credentials → Token Request → Token Caching → Authenticated Requests
```

**Process**:
1. **Credential Validation**: Verifies client ID and secret
2. **Token Request**: Requests access token from OAuth provider
3. **Token Management**: Handles token expiration and refresh
4. **Scope Management**: Manages OAuth scopes and permissions

## Test Scenario Coverage

### Endpoint-Specific Scenarios

#### GET Endpoints
- **Single Resource Retrieval**: Tests individual resource access
- **Collection Listing**: Tests paginated data retrieval
- **Filtered Queries**: Tests query parameter combinations
- **Cache Behavior**: Tests caching headers and behavior

#### POST Endpoints
- **Resource Creation**: Tests new resource creation with valid data
- **Validation Testing**: Tests input validation and error responses
- **Bulk Operations**: Tests multiple resource creation
- **File Uploads**: Tests multipart form data handling

#### PUT/PATCH Endpoints
- **Full Updates**: Tests complete resource replacement
- **Partial Updates**: Tests incremental resource modification
- **Conflict Resolution**: Tests concurrent update scenarios
- **Version Control**: Tests optimistic locking mechanisms

#### DELETE Endpoints
- **Resource Deletion**: Tests resource removal
- **Cascade Operations**: Tests related resource cleanup
- **Soft Deletes**: Tests logical deletion patterns
- **Permission Testing**: Tests deletion authorization

### Cross-Cutting Scenarios

#### Error Handling
- **4xx Client Errors**: Tests invalid requests and responses
- **5xx Server Errors**: Tests server error handling and recovery
- **Network Errors**: Tests timeout and connection handling
- **Rate Limiting**: Tests API rate limit responses

#### Performance Patterns
- **Cold Start Testing**: Tests initial request performance
- **Cache Warming**: Tests performance after cache population
- **Database Load**: Tests performance under database stress
- **CDN Behavior**: Tests content delivery network interactions

## Monitoring and Analysis

### Real-Time Metrics

During test execution, the framework provides:

1. **Request Metrics**
   - Requests per second (RPS)
   - Response time percentiles (50th, 95th, 99th)
   - Success/failure rates per endpoint
   - Concurrent user count

2. **Authentication Metrics**
   - Authentication success rate
   - Token refresh frequency
   - Authentication error types
   - Session duration statistics

3. **Error Analysis**
   - HTTP status code distribution
   - Error message categorization
   - Failure pattern identification
   - Recovery time measurement

### Post-Test Analysis

After test completion:

1. **Performance Summary**
   - Overall system performance metrics
   - Endpoint-specific performance analysis
   - Bottleneck identification
   - Capacity recommendations

2. **Authentication Analysis**
   - Authentication flow performance
   - Token management efficiency
   - Security issue identification
   - Optimization recommendations

3. **Error Reports**
   - Comprehensive error categorization
   - Root cause analysis
   - Recovery pattern analysis
   - Stability recommendations

## Configuration for Different Testing Types

### Development Testing
```env
MAX_USERS=5
SPAWN_RATE=1
RUN_TIME=5m
SPEC_INCLUDE_TAGS=core
```

### Staging Testing
```env
MAX_USERS=25
SPAWN_RATE=3
RUN_TIME=15m
SPEC_EXCLUDE_TAGS=admin
```

### Production Testing
```env
MAX_USERS=50
SPAWN_RATE=5
RUN_TIME=30m
SPEC_INCLUDE_TAGS=public
SAFETY_MODE=true
```

## Advanced Testing Features

### Tag-Based Testing
Control which endpoints to test based on OpenAPI tags:
```env
SPEC_INCLUDE_TAGS=users,orders    # Only test user and order endpoints
SPEC_EXCLUDE_TAGS=admin,delete    # Skip admin and delete operations
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
BACKOFF_FACTOR=2      # Exponential backoff multiplier
```

## Safety and Best Practices

### Pre-Test Validation
1. **Configuration Verification**: Validates all parameters before testing
2. **Connectivity Testing**: Tests API accessibility and authentication
3. **Specification Validation**: Verifies OpenAPI specification completeness
4. **Safety Limit Checks**: Ensures conservative load settings

### During Testing
1. **Real-Time Monitoring**: Continuous performance and error monitoring
2. **Automatic Throttling**: Reduces load on excessive error rates
3. **Resource Protection**: Monitors system resource usage
4. **Emergency Stop**: Provides immediate test termination capability

### Post-Test Analysis
1. **Comprehensive Reporting**: Detailed performance and error analysis
2. **Trend Analysis**: Historical performance comparison
3. **Optimization Recommendations**: Actionable improvement suggestions
4. **Security Review**: Authentication and authorization analysis

This comprehensive testing approach ensures reliable, safe, and insightful API load testing that evolves with your API documentation and provides actionable performance insights.