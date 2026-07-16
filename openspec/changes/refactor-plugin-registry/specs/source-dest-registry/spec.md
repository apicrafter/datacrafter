## ADDED Requirements

### Requirement: Decorator-Based Source & Destination Registry
Sources and destinations SHALL register themselves via a decorator
(`@register_source` / `@register_destination`) into a module-level registry, and the
factory functions SHALL resolve a config `type` by registry lookup rather than an
if/elif chain.

#### Scenario: known type resolves
- **WHEN** `get_source_from_file` is called with `stype="file-csv"`
- **THEN** it returns an instance of the CSV source class registered under that name

#### Scenario: unknown type raises a clear error
- **WHEN** `get_source_from_file` is called with an unrecognized `stype`
- **THEN** it raises `UnknownSourceTypeError` whose message lists the registered source types

### Requirement: Discoverable Type Catalog
The system SHALL expose `list_sources()` and `list_destinations()` returning all
registered type names, for use by tooling such as `config schema`.

#### Scenario: list registered sources
- **WHEN** `list_sources()` is called
- **THEN** it returns a collection containing every registered source type name (e.g. `file-csv`, `file-jsonl`)
