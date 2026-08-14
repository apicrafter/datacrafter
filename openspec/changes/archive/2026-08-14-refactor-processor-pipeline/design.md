## Context
`CommonProcessor.run()` mixes iteration, per-record transformation, error handling,
buffering, and writing in one 180-line method with duplicated branches.

## Goals / Non-Goals
- Goals: each helper does one thing and is independently testable; eliminate the
  buffered/unbuffered duplication; make error strategy explicit.
- Non-Goals: changing the processor's public API or config schema; async/concurrency.

## Decisions
- **Unified buffered path:** always buffer; `buffer_size=1` reproduces unbuffered
  behavior. One write code path instead of two.
- **Extract helpers** as private methods on `CommonProcessor` (keep state together).
- **Error strategy:** honor `ERROR_STRATEGY_RETRY` (retry on `RecordProcessingError`
  up to `DEFAULT_MAX_RETRIES`) and `ERROR_STRATEGY_SKIP` (default). Remove dead code
  that can never trigger.

## Risks / Trade-offs
- Behavior must stay identical for the happy path and for per-record failures.
  Mitigation: rely on the existing integration test and add focused unit tests for
  each helper before refactoring (characterization tests).

## Migration Plan
1. Add characterization tests for current `run()` behavior (success, skip-on-error,
   autoid, autotype).
2. Extract helpers one at a time, running tests after each.
3. Collapse buffered/unbuffered branches last.

## Open Questions
- Should `buffer_size` default change from `DEFAULT_BULK_RECORDS`? Keep it unchanged
  to preserve behavior.
