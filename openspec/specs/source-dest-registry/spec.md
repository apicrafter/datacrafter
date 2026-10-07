# source-dest-registry Specification

## Purpose
Sources, destinations, and extractors register by type name so factories and
`datacrafter config schema` can discover them without a hardcoded type list.
## Requirements
### Requirement: Decorator-Based Source & Destination Registry
Sources and destinations SHALL register themselves via a decorator
(`@register_source` / `register_destination`) into a module-level registry. Each
registered class SHALL own its construction through a `from_config` classmethod that
validates its own required options, and the factory functions SHALL consist of
registry lookup plus delegation to `from_config` — they MUST NOT contain per-type
constructor branches (if/elif chains) or unreachable fallback raises.

#### Scenario: known type resolves
- **WHEN** `get_source_from_file` is called with `stype="csv"`
- **THEN** it returns an instance of the CSV source class registered under that name

#### Scenario: unknown type raises a clear error
- **WHEN** `get_source_from_file` is called with an unrecognized `stype`
- **THEN** it raises `UnknownSourceTypeError` whose message lists the registered source types

#### Scenario: new plugin needs no factory edit
- **WHEN** a new source class is defined with `@register_source("mytype")` and a
  `from_config` classmethod
- **THEN** it is constructible through the factory without modifying any factory code

### Requirement: Discoverable Type Catalog
The system SHALL expose `list_sources()`, `list_destinations()`, and
`list_extractors()` returning all registered type names, for use by tooling such
as `config schema`.

#### Scenario: list registered sources
- **WHEN** `list_sources()` is called
- **THEN** it returns a collection containing every registered source type name (e.g. `csv`, `jsonl`)

### Requirement: Parquet File Destination
The system SHALL register destination type `file-parquet`. Construction MUST work
when pyarrow is installed and MUST raise a clear ImportError when it is not.

#### Scenario: parquet is listed
- **WHEN** `list_destinations()` is called
- **THEN** the result includes `file-parquet`

### Requirement: Decorator-Based Extractor Registry
Extractors SHALL register themselves via `@register_extractor` into the shared
plugin registry. `get_extractor` SHALL construct the class for a config `type`,
and an unknown type MUST raise `UnknownExtractorTypeError` listing registered names.

#### Scenario: known extractor type resolves
- **WHEN** `get_extractor` is called with `type: file-csv`
- **THEN** it returns a file extractor instance registered under that name

#### Scenario: unknown extractor type
- **WHEN** `get_extractor` is called with an unrecognized type
- **THEN** it raises `UnknownExtractorTypeError` whose message lists registered extractor types

#### Scenario: list extractors
- **WHEN** `list_extractors()` is called
- **THEN** the result includes `file-csv`, `api`, `code`, `rss`, and `dcat`

### Requirement: Extractor Run Template Method
`BaseExtractor.run()` SHALL be a template method performing validation, result reset,
delegation to a subclass `_execute()` implementation, and state commit; each extractor
subclass SHALL own its mode's execution logic, and identical `run()` bodies MUST NOT
be duplicated across subclasses.

#### Scenario: each extractor type runs its own mode logic
- **WHEN** any registered extractor type runs
- **THEN** validation and state commit happen exactly once via the base template
  method and the type-specific execution logic lives in that extractor's class

#### Scenario: no duplicated run bodies
- **WHEN** extractor subclasses are inspected
- **THEN** none re-implement the validation/reset/commit sequence already provided by
  the base template method

