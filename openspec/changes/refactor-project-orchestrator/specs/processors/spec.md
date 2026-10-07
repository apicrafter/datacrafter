## ADDED Requirements
### Requirement: Processor Config Independence
`CommonProcessor` SHALL accept a self-contained processor configuration (a typed
`ProcessorConfig`) plus explicit paths, and MUST NOT read configuration, paths, or
state from the `Project` orchestrator object. Constructing and running a processor
with only its config and paths SHALL be possible without instantiating `Project`.

#### Scenario: processor runs without Project
- **WHEN** a test constructs `CommonProcessor` with a `ProcessorConfig` and explicit
  output/state paths and runs it over a source and destination
- **THEN** it processes records successfully with no `Project` instance involved

#### Scenario: config normalization is preserved
- **WHEN** `autoid_fields` is provided as a comma-separated string or as a list
- **THEN** the processor normalizes both forms identically to the current behavior
