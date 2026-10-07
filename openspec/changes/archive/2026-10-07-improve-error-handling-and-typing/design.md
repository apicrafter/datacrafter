## Context
Logging is configured in three places with conflicting intents; exceptions form six
unrelated families; and load-path failures are logged as warnings so a run whose data
never landed can report success. Typing coverage is 17% of functions and mypy checks 3
files, so contract drift is invisible.

## Goals / Non-Goals
- Goals: one logging owner; a single exception root; write failures fail the run;
  whole-package mypy in non-strict mode.
- Non-Goals: strict typing (`--strict`), structured logging, or changing CLI flags.

## Decisions
- Decision: a new `datacrafter/errors.py` defines `DataCrafterError`. New module rather
  than reusing an existing one so that importing the exception base never drags in
  CLI/registry dependencies.
  - Alternatives: rooting on `ProcessingError` (couples I/O errors to processor
    semantics) or keeping per-family roots (status quo — no common handler).
- Decision: `Unknown*TypeError` re-parents from `KeyError` to `DataCrafterError`
  because nothing catches them as `KeyError`; `KeyError` only adds quoted-message
  rendering noise.
- Decision: import-time logging configuration is removed; the Typer CLI callback and
  `__main__` become the single level owner. Library consumers get the stdlib default
  (lastResort) instead of a hijacked root logger.
- Decision: failure propagation boundary is `Project.run`: destinations raise
  `DataCrafterError` subclasses; `Project.run` catches once, marks the stage failed in
  `state.json`, returns a non-zero exit; cleanup `close()` remains best-effort.
- Decision: mypy non-strict over the whole package now, strict ratcheted later per
  module.

## Risks / Trade-offs
- Runs that previously "succeeded" with invisible write failures will now fail →
  intended behavior change; note prominently in CHANGELOG under a minor bump.
- Re-parenting exceptions can break callers that catch `KeyError` → grep shows only
  internal raises/tests; document in CHANGELOG.
- Removing import-time logging config changes what library users see (no handlers
  until they configure logging) → stdlib `lastResort` still prints warnings+.

## Migration Plan
1. Add `errors.py` + re-parent (internal mechanical change).
2. Logging owner consolidation.
3. Failure propagation + state reporting.
4. Typing widening (independent; can land separately).
Rollback: each step is an isolated commit; revert individually if needed.

## Open Questions
- Should `RecordProcessingError` remain public API or fold into `ProcessingError`?
- Which mypy strictness flags to ratchet first (likely `disallow_untyped_defs` on
  `common/`)?
