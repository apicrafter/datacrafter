# code-quality Specification

## Purpose
Shared constants, logging, exception handling, and public protocols stay consistent so the package does not silently swallow errors or drift.
## Requirements
### Requirement: Single Source of Truth for Constants
Shared constants (e.g. retry defaults) SHALL be defined once in `constants.py` and
imported elsewhere; modules MUST NOT redefine duplicated copies that can drift.
Constants that no production code imports SHALL be deleted rather than kept as dead
metadata.

#### Scenario: no duplicated constant definitions
- **WHEN** the package is searched for `DEFAULT_MAX_RETRIES`
- **THEN** it is defined in exactly one module (`constants.py`) and imported elsewhere

#### Scenario: no unused constants
- **WHEN** every constant in `constants.py` is cross-referenced against package imports
- **THEN** each is imported by at least one production module

### Requirement: Type-Annotated Public Protocols
The abstract base classes (`BaseSource`, `BaseFileSource`, `BaseDestination`, `BaseFileDestination`, `BaseDBDestination`, `BaseSearchDestination`) MUST carry type annotations on their method signatures to document the public protocol.

#### Scenario: base class methods annotated
- **WHEN** a base source/destination class is inspected
- **THEN** its method signatures include parameter and return-type annotations

### Requirement: No Silent Exception Suppression
The codebase MUST NOT swallow exceptions with bare `except Exception: pass`; suppressed
exceptions SHALL be logged at DEBUG or handled with the narrowest practical exception type.

#### Scenario: exception is logged not silenced
- **WHEN** an exception occurs in a destination close/cleanup path that was previously `except Exception: pass`
- **THEN** the exception is logged (at least at DEBUG level) rather than silently ignored

### Requirement: Consistent Logging Configuration
Logging SHALL be configured in a single place: the CLI entry path owns the root logger
level and handlers, and no module SHALL configure the root logger as an import side
effect. `Project.enable_logging` SHALL add its rotating file handler without removing
handlers or levels already installed by the embedding application. The logging-level
logic MUST NOT contain no-op tautologies (e.g. a conditional whose two branches return
the same value).

#### Scenario: importing core does not touch the root logger
- **WHEN** `datacrafter.core` is imported into a fresh interpreter
- **THEN** the root logger level and handlers are unchanged from their pre-import state

#### Scenario: project logging preserves external handlers
- **WHEN** an application has configured its own root handler and constructs a `Project`
- **THEN** that handler still receives records after project logging is enabled

#### Scenario: no logging-config tautology
- **WHEN** the verbose-level logic in `Project.enable_logging` is inspected
- **THEN** the conditional produces different values for its branches based on the current log level

### Requirement: Correct Identifier Spelling
Identifiers and docstrings SHALL be free of obvious typos (e.g. `DEFAILT_CONFIG`,
"indexedr").

#### Scenario: no typo identifiers
- **WHEN** the package is searched for known typos
- **THEN** no occurrences of `DEFAILT_CONFIG` or `indexedr` remain

### Requirement: Single Style-Lint Configuration Owner
Style linting SHALL be owned by exactly one tool configuration (ruff in
`pyproject.toml`); no duplicate or conflicting legacy lint configuration files (e.g. a
root `flake8` file and a `[flake8]` section in `setup.cfg`) SHALL remain in the
repository.

#### Scenario: no conflicting lint configs
- **WHEN** the repository root is inspected for lint configuration
- **THEN** style rules are defined only in `pyproject.toml` under `[tool.ruff]`

### Requirement: No IDE or Scratch Artifacts Tracked
The repository SHALL NOT track IDE state (`.idea/`) or personal scratch documents;
durable working notes live under versioned documentation directories instead.

#### Scenario: clean tracked file list
- **WHEN** `git ls-files` is inspected
- **THEN** it contains no `.idea/` entries and no superseded scratch notes

### Requirement: No Dead Code in Shipped Modules
Functions, methods, and constants in the shipped package SHALL have at least one
production call site (or be part of a documented public API); legacy conversion suites
superseded by the source classes, unreachable branches, commented-out code blocks, and
defensive guards around stdlib imports MUST be removed.

#### Scenario: source read_bulk is gone or used
- **WHEN** source classes are inspected for `read_bulk`
- **THEN** either no implementation exists or at least one production caller does

#### Scenario: capability tables reflect reality
- **WHEN** `SUPPORTED_COMPRESSION` (or its replacement) reports a codec as supported
- **THEN** a handler branch for that codec exists, and codecs without handlers are
  reported as unsupported

### Requirement: Shared Exception Root
All public package exceptions (`ProcessingError`, `RecordProcessingError`,
`DataCrafterConfigurationError`, `MissingEnvVarError`, `UnknownSourceTypeError`,
`UnknownDestinationTypeError`, `UnknownExtractorTypeError`) SHALL derive from a common
`DataCrafterError` base so callers can catch package failures with one type.

#### Scenario: single catch handles package errors
- **WHEN** any of the listed exceptions is raised
- **THEN** it is an instance of `DataCrafterError`

### Requirement: Write Failures Fail the Run
Errors while writing, flushing, or closing a destination SHALL propagate to the
pipeline orchestrator, mark the affected stage failed in `state.json`, and produce a
non-zero exit code; cleanup of already-failed resources MAY remain best-effort with a
debug log. A run whose data failed to load MUST NOT report success.

#### Scenario: destination write error fails the stage
- **WHEN** a destination raises while writing records
- **THEN** the run exits non-zero and `state.json` records the destination stage as
  failed with the error text

#### Scenario: close error after successful write fails loudly
- **WHEN** finalizing a ZIP destination raises on close
- **THEN** the run is marked failed rather than completing with a warning

### Requirement: Package-Wide Static Typing Gate
Static type checking SHALL cover the entire `datacrafter` package (starting
non-strict), run in CI, and the abstract base class signatures SHALL be fully
annotated so plugin contracts are typed.

#### Scenario: mypy covers the package
- **WHEN** CI runs the configured mypy invocation
- **THEN** it checks every module under `datacrafter/` and passes

