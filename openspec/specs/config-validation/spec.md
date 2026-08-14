# config-validation Specification

## Purpose
Validate `datacrafter.yml` against registered extractor, source, and destination
types before a pipeline runs, and keep trusted custom scripts inside the project tree.
## Requirements
### Requirement: Project Configuration Validation
The system SHALL validate a loaded `datacrafter.yml` before pipeline execution
and MUST reject unknown extractor types, destination types, extractor methods,
and processor error strategies with messages that list the supported values.

#### Scenario: unknown destination type
- **WHEN** `datacrafter check` is run against a config whose `destination.type` is not registered
- **THEN** validation fails and the error lists registered destination types including `file-jsonl` and `couchdb`

#### Scenario: init stub is incomplete
- **WHEN** `datacrafter check` is run immediately after `datacrafter init` with no extractor section
- **THEN** validation fails because the required `extractor` key is missing

#### Scenario: valid config passes
- **WHEN** a config includes required keys, a known extractor type/method, and a registered destination type with `fileprefix` for file destinations
- **THEN** validation succeeds

### Requirement: CouchDB Destination Registration
The system SHALL register CouchDB as a destination type `couchdb` alongside MongoDB,
ArangoDB, and Meilisearch, and MUST construct it from destination config.

#### Scenario: couchdb type is listed
- **WHEN** `list_destinations()` is called
- **THEN** the result includes `couchdb`

### Requirement: Project-Local Trusted Scripts
Custom extractor and processor Python scripts SHALL resolve to a real file inside
the project directory. Paths that escape the project tree MUST be rejected.

#### Scenario: script outside project
- **WHEN** a `code` extractor or custom processor script path resolves outside the project directory
- **THEN** the system raises an error and does not execute the file

### Requirement: Extractors List
A project MAY declare `extractors` as a list of extractor objects instead of a
single `extractor`. Validation SHALL accept either form. At least one extractor
MUST be present.

#### Scenario: extractors list validates
- **WHEN** a config has `extractors` with two valid extractor objects and no singular `extractor`
- **THEN** validation succeeds

#### Scenario: neither extractor nor extractors
- **WHEN** a config omits both `extractor` and `extractors`
- **THEN** validation fails

