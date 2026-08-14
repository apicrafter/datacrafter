## ADDED Requirements

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
