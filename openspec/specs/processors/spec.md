# processors Specification

## Purpose
The processor transforms records through a pipeline of steps and writes them with a single buffered path and an explicit error strategy.
## Requirements
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

#### Scenario: retry then succeed
- **WHEN** a record fails to process, the error strategy is retry, and a later attempt succeeds
- **THEN** the record is written and is not counted as failed

### Requirement: Autotype Inference
When `processor.config.autotype` is true, the processor SHALL sample records,
infer field types (`int`, `float`, `bool`, `date`, `datetime`), and apply those
conversions. An explicit `typemap` MUST override inferred types for the same
fields. Autotype MUST NOT run unless the flag is true.

#### Scenario: inferred int conversion
- **WHEN** autotype is true and sampled values for a field are integer-like strings
- **THEN** those values are converted to integers in the written records

#### Scenario: explicit typemap wins
- **WHEN** autotype infers `int` for a field and `typemap` sets that field to `float`
- **THEN** the written value is a float

### Requirement: Stable Autoid
When `processor.config.autoid` is true, the processor SHALL set `_id` on each
record that does not already have `_id`. The identifier MUST be derived from
`autoid_fields` when configured, otherwise from a hash of canonical JSON.
Autoid MUST default to false.

#### Scenario: hash id when enabled
- **WHEN** autoid is true and the record has no `_id`
- **THEN** the written record includes a non-empty `_id` string

#### Scenario: disabled by default
- **WHEN** autoid is not set in config
- **THEN** the written record does not gain an `_id` field

### Requirement: Failed-Record Sidecar
When a record is skipped or fails during processing, the processor SHALL append
it to `output/errors.jsonl` (when the project has an output directory) and
include the sidecar path in processor stage results.

#### Scenario: skipped record is captured
- **WHEN** error strategy is skip and a record fails a pipeline step
- **THEN** `output/errors.jsonl` contains a line with the original record and error text

