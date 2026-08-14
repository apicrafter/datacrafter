# Change: Decompose Oversized Processor Methods

## Why
`CommonProcessor.run()` at `processors/base.py:328-509` is ~180 lines with deeply
nested try/except/for blocks and a near-duplicate buffered-vs-unbuffered write path.
This is hard to test, hard to reason about, and a hotspot for the bugs surfaced in
`fix-latent-code-bugs`. The retry logic is also dead in practice (only retries
`RecordProcessingError`, which the pipeline rarely raises).

## What Changes
- Extract focused helpers: `_iter_records(source)`, `_process_single(record)`,
  `_write_record(destination, record)`, `_flush_buffer(destination, buffer)`.
- Collapse the duplicated buffered/unbuffered write branches into one path that uses
  a buffer of configurable size (size 1 = unbuffered).
- Clarify the retry/error-strategy: branch on `ERROR_STRATEGY_RETRY` constant
  (currently defined but unused) or remove dead retry code.
- Preserve observable behavior (record ordering, error logging, autoid/autotype).

## Impact
- Affected specs: `processors`
- Affected code: `datacrafter/processors/base.py`
- Risk: medium — central pipeline path; must keep integration test (JSONL→JSONL) green.
