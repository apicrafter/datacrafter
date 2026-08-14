## ADDED Requirements

### Requirement: Focused Processor Helper Methods
`CommonProcessor.run()` SHALL be decomposed into focused helper methods (record
iteration, single-record processing, writing, buffer flushing), each independently
testable, and `run()` itself SHALL remain under approximately 60 lines.

#### Scenario: run delegates to helpers
- **WHEN** `CommonProcessor.run()` processes a batch of records
- **THEN** iteration, per-record transformation, and writing each occur in dedicated helper methods rather than inline in `run()`

### Requirement: Unified Buffering Path
The processor SHALL use a single code path for writing records that supports a
configurable buffer size, where a buffer size of 1 reproduces unbuffered behavior,
eliminating the duplicated buffered/unbuffered branches.

#### Scenario: unbuffered write via buffer size one
- **WHEN** the processor runs with `buffer_size=1`
- **THEN** each processed record is written immediately, producing output identical to the former unbuffered path

### Requirement: Explicit Error Strategy
The processor SHALL honor a configured error strategy (retry or skip) for record
processing failures and MUST NOT contain dead retry code that can never trigger.

#### Scenario: skip on error
- **WHEN** a record fails to process and the error strategy is skip
- **THEN** the failure is logged, the record is skipped, and processing continues with the next record
