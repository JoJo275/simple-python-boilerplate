# Tests

Test suite for the project.

## Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   └── test_*.py
└── integration/       # Integration tests (database, external services)
    ├── test_*.py
    └── sql/           # SQL fixtures for integration tests
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=simple_python_boilerplate

# Run a specific test file
pytest tests/unit/test_example.py

# Run a specific test
pytest tests/unit/test_example.py::test_placeholder
```

## Writing Tests

- Place unit tests in [tests/unit/](unit/)
- Place integration tests in [tests/integration/](integration/)
- Name test files `test_*.py`
- Name test functions `test_*`

See [pytest documentation](https://docs.pytest.org/) for more details.

## Related

- [pyproject.toml](../pyproject.toml) — pytest configuration (`[tool.pytest.ini_options]`)
- [ADR 006: pytest](../docs/adr/006-pytest-for-testing.md) — Why we use pytest

<!-- TODO: Update this README with your project's testing conventions -->
