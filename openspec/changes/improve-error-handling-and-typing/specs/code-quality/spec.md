## MODIFIED Requirements
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

## ADDED Requirements
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
