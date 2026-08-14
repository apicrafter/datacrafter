# source-dest-registry Specification

## Purpose
Sources, destinations, and extractors register by type name so factories and
`datacrafter config schema` can discover them without a hardcoded type list.

## Requirements
### Requirement: Decorator-Based Source & Destination Registry
Sources and destinations SHALL register themselves via a decorator
(`@register_source` / `@register_destination`) into a module-level registry, and the
factory functions SHALL resolve a config `type` by registry lookup rather than an
if/elif chain.

#### Scenario: known type resolves
- **WHEN** `get_source_from_file` is called with `stype="csv"`
- **THEN** it returns an instance of the CSV source class registered under that name

#### Scenario: unknown type raises a clear error
- **WHEN** `get_source_from_file` is called with an unrecognized `stype`
- **THEN** it raises `UnknownSourceTypeError` whose message lists the registered source types

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

