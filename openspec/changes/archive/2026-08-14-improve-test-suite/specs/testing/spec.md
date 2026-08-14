## ADDED Requirements

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
