## ADDED Requirements

### Requirement: Data Package Sidecar
After a successful file destination write, the system SHALL write `datapackage.json`
in the output directory describing the written resource and inferred field types,
unless `destination.datapackage` is false.

#### Scenario: jsonl gets a data package
- **WHEN** a pipeline writes JSONL to `output/` and datapackage is not disabled
- **THEN** `output/datapackage.json` exists and lists that JSONL file as a resource
