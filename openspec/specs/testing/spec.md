# testing Specification

## Purpose
Tests are real pytest modules, mock external services, cover public CLI commands, and keep coverage configuration in one place.
## Requirements
### Requirement: External Backends Tested via Mocks
Each database/search destination (MongoDB, ArangoDB, CouchDB, Meilisearch) SHALL have
unit tests that exercise its write path against a mocked driver client, so backends
are tested without requiring live services.

#### Scenario: mongo destination write
- **WHEN** the MongoDB destination writes a batch of records
- **THEN** a test asserts `insert_many` is called with the expected documents against a mocked collection

### Requirement: Network Layer Tested Without Real Calls
The data collection module (`common/collect.py`) SHALL be covered by tests that mock
HTTP requests and the external downloader, so no test makes real network calls.

#### Scenario: download with mocked requests
- **WHEN** `get_file` is tested
- **THEN** `requests.get` is mocked and no real HTTP request leaves the test process

### Requirement: CLI Commands Tested
Every public Typer command in `core.py` SHALL have at least one test using a CLI test
runner (e.g. `typer.testing.CliRunner`) verifying exit code and basic output.

#### Scenario: config validate command
- **WHEN** the `config validate` command is invoked with a valid config
- **THEN** it exits 0 and reports success

### Requirement: Real Pytest Tests Only
All files under `tests/` SHALL be valid pytest test modules using assertions; no test
file SHALL use `print()` for pass/fail reporting or `sys.exit()` as an assertion
mechanism.

#### Scenario: no script-style tests
- **WHEN** the tests directory is scanned
- **THEN** every test function uses `assert` or pytest constructs and none call `sys.exit`

### Requirement: Single Source of Coverage Configuration
Coverage configuration SHALL live in exactly one place (`.coveragerc`), and `pytest.ini`
MUST NOT contain a conflicting `[coverage:*]` block.

#### Scenario: no duplicate coverage config
- **WHEN** test configuration files are inspected
- **THEN** coverage settings appear only in `.coveragerc`

### Requirement: Hermetic Test Collection
The test suite SHALL be collectable in a clean environment containing only the declared
runtime and dev dependencies, with optional-dependency test modules skipped (via
`pytest.importorskip` or equivalent) rather than failing collection with `ImportError`.

#### Scenario: collection without zstandard installed
- **WHEN** pytest collects the suite in an environment where `zstandard` is not
  installed
- **THEN** zst-related tests are skipped and collection reports no errors

### Requirement: Parametrized Input Grids
Repeated input grids (compression codecs × formats × config keys, converter edge
cases) SHALL be covered with `pytest.mark.parametrize` (or property-based tests where
appropriate) instead of copy-pasted near-identical test functions.

#### Scenario: compression matrix is one parametrized test
- **WHEN** the compression test module is inspected
- **THEN** the format × codec × config-key grid is expressed as a single parametrized
  test function with a data table

### Requirement: Accurate Marker and Configuration Documentation
Declared pytest markers SHALL correspond to tests that actually carry them, documented
commands in `tests/README.md` SHALL select a non-empty set, and default `addopts` MUST
NOT write coverage artifacts or log files into the repository root during ordinary
local runs.

#### Scenario: documented marker selects tests
- **WHEN** a marker documented in `tests/README.md` is used with `pytest -m`
- **THEN** it selects the intended non-empty set of tests

#### Scenario: local run leaves no artifacts
- **WHEN** a developer runs bare `pytest` locally
- **THEN** no `.coverage`, `coverage.xml`, `htmlcov/`, or `pytest.log` is created in
  the repository root

### Requirement: Shared Fixtures Live in conftest
Test helpers used by more than one module (e.g. the recording destination) SHALL be
defined once in `conftest.py`, and unused fixtures MUST be removed.

#### Scenario: recording destination defined once
- **WHEN** the tests directory is searched for the recording-destination class
- **THEN** it is defined exactly once in `conftest.py` and imported by its users

