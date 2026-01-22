# Unit Tests for Security Pipeline Demo

This directory contains comprehensive unit tests for the security pipeline components.

## Test Structure

### `test_security_pipeline.py`
- **Database Operations**: Tests for database connection and initialization
- **Flask Routes**: Tests for all route functions with mocking
- **SAST Scanning**: Tests for Bandit integration
- **DAST Scanning**: Tests for OWASP ZAP integration
- **Pipeline Orchestration**: Tests for the main security pipeline

### `test_flask_app.py`
- **Flask App Testing**: Full integration tests using Flask test client
- **Route Testing**: HTTP request/response testing for all endpoints
- **Security Validation**: Tests for proper handling of security vulnerabilities

## Running Tests

### Prerequisites
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
pytest test_security_pipeline.py
pytest test_flask_app.py
```

### Run Specific Test Classes
```bash
pytest test_security_pipeline.py::TestDatabaseOperations
pytest test_flask_app.py::TestFlaskAppSecurityHeaders
```

### Run With Coverage
```bash
pytest --cov=. --cov-report=html
```

## Test Coverage

The tests cover:

1. **Database Functions**
   - Connection establishment
   - Schema initialization
   - Data insertion

2. **Flask Routes**
   - User profile retrieval (including SQL injection attempts)
   - Connectivity testing (including command injection attempts)
   - Hash generation
   - Knowledge base search
   - Admin dashboard
   - System configuration display

3. **Security Scanning**
   - SAST with Bandit (success/failure scenarios)
   - DAST with OWASP ZAP (success/failure scenarios)
   - Report generation

4. **Pipeline Orchestration**
   - Full pipeline execution
   - SAST-only execution
   - Error handling and cleanup

## Mocking Strategy

Tests use extensive mocking to:
- Avoid actual database operations
- Prevent real network calls
- Mock subprocess calls for security tools
- Simulate file system operations

## Security Test Validation

Tests specifically validate that the application:
- Properly handles SQL injection attempts
- Blocks command injection attempts
- Correctly exposes credentials in the config endpoint (by design)
- Generates proper security reports

## Continuous Integration

These tests can be integrated into CI/CD pipelines to ensure code quality and security validation.
