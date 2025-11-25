# Datacrafter Test Suite

This directory contains the test suite for datacrafter.

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=datacrafter --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_common.py
```

### Run specific test
```bash
pytest tests/test_common.py::TestGetDictValue::test_simple_key
```

### Run by marker
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_common.py` - Tests for common utility functions
- `test_state.py` - Tests for ProjectState
- `test_sources.py` - Tests for source classes
- `test_destinations.py` - Tests for destination classes
- `test_processors.py` - Tests for processor classes
- `test_mappers.py` - Tests for mapper functions
- `test_project.py` - Tests for Project class
- `test_integration.py` - Integration tests for ETL pipelines

## Fixtures

Common fixtures available in `conftest.py`:
- `temp_dir` - Temporary directory for test files
- `sample_project` - Sample project instance
- `sample_config` - Sample project configuration
- `sample_jsonl_data` - Sample JSONL data
- `sample_csv_data` - Sample CSV data
- `jsonl_file` - Temporary JSONL file
- `csv_file` - Temporary CSV file
- `state_file` - Temporary state file
- `empty_state` - Empty project state

## Coverage

Target coverage: 80%+

View coverage report:
```bash
pytest --cov=datacrafter --cov-report=html
open htmlcov/index.html
```

