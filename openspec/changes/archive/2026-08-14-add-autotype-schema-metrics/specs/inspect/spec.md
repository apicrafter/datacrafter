## ADDED Requirements

### Requirement: Dry-Run Plan
`datacrafter run --dry-run` SHALL validate the project configuration, print the
resolved extractor, processor flags, and destination, and MUST NOT download
sources or write destination files.

#### Scenario: dry-run writes nothing
- **WHEN** `datacrafter run --dry-run` is invoked on a valid project
- **THEN** the command exits 0, prints a plan that includes the destination type, and creates no new files under `output/`

### Requirement: Schema Command
`datacrafter schema` SHALL infer field types from JSONL records in `output/`
(falling back to `current/`) and print them. If no JSONL files exist, it MUST
exit non-zero with a message to run the pipeline first.

#### Scenario: schema from output jsonl
- **WHEN** `output/` contains JSONL records with an integer-like field
- **THEN** `datacrafter schema` exits 0 and reports that field's inferred type

### Requirement: Metrics Command
`datacrafter metrics` SHALL print record counts, per-field null counts, and
top-value histograms from the same JSONL files as `schema`.

#### Scenario: metrics histograms
- **WHEN** `output/` contains JSONL records
- **THEN** `datacrafter metrics` exits 0 and reports the total record count
