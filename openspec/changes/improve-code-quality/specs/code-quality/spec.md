## ADDED Requirements

### Requirement: Single Source of Truth for Constants
Shared constants (e.g. `SUPPORTED_FILE_TYPES`, retry defaults) SHALL be defined once
in `constants.py` and imported elsewhere; modules MUST NOT redefine duplicated copies
that can drift.

#### Scenario: no duplicated constant definitions
- **WHEN** the package is searched for `SUPPORTED_FILE_TYPES` and `DEFAULT_MAX_RETRIES`
- **THEN** each is defined in exactly one module (`constants.py`) and imported elsewhere

### Requirement: Type-Annotated Public Protocols
The abstract base classes (`BaseSource`, `BaseFileSource`, `BaseDestination`, `BaseFileDestination`, `BaseDBDestination`, `BaseSearchDestination`) MUST carry type annotations on their method signatures to document the public protocol.

#### Scenario: base class methods annotated
- **WHEN** a base source/destination class is inspected
- **THEN** its method signatures include parameter and return-type annotations

## MODIFIED Requirements

### Requirement: No Silent Exception Suppression
The codebase MUST NOT swallow exceptions with bare `except Exception: pass`; suppressed
exceptions SHALL be logged at DEBUG or handled with the narrowest practical exception type.

#### Scenario: exception is logged not silenced
- **WHEN** an exception occurs in a destination close/cleanup path that was previously `except Exception: pass`
- **THEN** the exception is logged (at least at DEBUG level) rather than silently ignored

### Requirement: Consistent Logging Configuration
Logging SHALL be configured in a single place, and the logging-level logic MUST NOT
contain no-op tautologies (e.g. a conditional whose two branches return the same value).

#### Scenario: no logging-config tautology
- **WHEN** the verbose-level logic in `Project.enable_logging` is inspected
- **THEN** the conditional produces different values for its branches based on the current log level

### Requirement: Correct Identifier Spelling
Identifiers and docstrings SHALL be free of obvious typos (e.g. `DEFAILT_CONFIG`,
"indexedr").

#### Scenario: no typo identifiers
- **WHEN** the package is searched for known typos
- **THEN** no occurrences of `DEFAILT_CONFIG` or `indexedr` remain
