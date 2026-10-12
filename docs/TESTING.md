# Testing Guide

## Test Suite

OrionAI includes a comprehensive test suite with >80% code coverage.

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions
└── api/            # API endpoint tests
```

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test categories:
```bash
pytest -m unit
pytest -m integration
pytest -m api
```

### Test Requirements

- Minimum coverage: 80%
- All external LLM calls are mocked
- Redis is mocked for unit tests
- Async tests supported via pytest-asyncio

### CI/CD

Tests run automatically on:
- Push to main/develop branches
- Pull requests to main

CI enforces:
- Test coverage >= 80%
- Linting with flake8
- Code formatting checks

### Docker Testing

Test the full Docker deployment:
```bash
./scripts/test_docker.sh
```

Or manually:
```bash
docker-compose up -d
docker exec orionai-cpu pytest
docker-compose down
```

## Development Tools

### Makefile Commands

```bash
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make coverage          # Generate coverage report
make lint              # Run linters
make format            # Format code
make docker-build      # Build Docker images
make docker-up         # Start services
make docker-down       # Stop services
```

### Pre-commit Checks

Before committing:
```bash
make lint
make test
```
