# OrionAI Test Suite

## Running Tests

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

## Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for component interactions
- `tests/api/` - API endpoint tests

## Coverage Requirements

Minimum coverage: 80%

The CI pipeline will fail if coverage drops below this threshold.
