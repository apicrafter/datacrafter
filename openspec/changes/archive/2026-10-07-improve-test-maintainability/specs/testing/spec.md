## ADDED Requirements
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
