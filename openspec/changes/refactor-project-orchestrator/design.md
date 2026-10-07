## Context
`Project` accumulates every orchestration concern (392 lines, ~15 responsibilities)
and `CommonProcessor` depends on five `project.*` attributes, coupling the transform
engine to the CLI orchestrator. Tests currently build full `Project` fixtures just to
exercise the processor.

## Goals / Non-Goals
- Goals: processor decoupled from `Project`; config loading testable in isolation;
  `Project.process` under ~40 lines; zero CLI/config/state behavior change.
- Non-Goals: pipeline DAG abstraction, async processing, plugin-stage model.

## Decisions
- Decision: `ProcessorConfig` dataclass rather than passing a dozen kwargs or the raw
  YAML dict — typed, defaultable, and it matches the existing
  `DEFAULT_CONFIG_PARAMS` keys one-to-one to avoid config renames.
  - Alternatives: keep `Project` param (status quo coupling); a generic `Context`
    object (stringly re-couples everything).
- Decision: config loading moves to `common/projectconfig.py` returning the same dict
  shape initially (interpolation + `safe_load` stay put), so the loader extraction is
  behavior-neutral; typing it comes with the typing change, not this one.
  - Alternatives: full pydantic-style schema now (scope creep; validation already
    exists in `common/validation.py`).
- Decision: `Project` keeps state ownership (`ProjectState`) and passes the state
  object into the processor explicitly — state is genuinely shared run context.

## Risks / Trade-offs
- Large-diff refactor on the hottest file → land after Phase 1/2 fixes, in small
  commits, gated by unchanged existing tests (behavior gate 2.1).
- Hidden coupling discovered mid-refactor (more `project.*` reads) → grep audit first
  (already done: five attributes at `processors/base.py:255-324`).

## Migration Plan
1. Extract config loader (no signature changes).
2. Extract logging.
3. Introduce `ProcessorConfig`, migrate `CommonProcessor`, update `Project`.
4. Decompose `Project.process`.
Rollback: each step independently revertible; no data or config migrations.

## Open Questions
- Should `ProcessorConfig` validation (e.g. `autoid_fields` string/list) live in the
  dataclass `__post_init__` instead of `CommonProcessor.__init__` normalization?
