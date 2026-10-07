## MODIFIED Requirements
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

## ADDED Requirements
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
