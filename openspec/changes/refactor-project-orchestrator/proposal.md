# Change: Refactor the Project orchestrator

## Why
`Project` (`cmds/project.py:61-453`) is a god object: config loading and env
interpolation, directory creation, logging configuration (including a nested
`JSONFormatter` class), state persistence, extractor/processor/destination wiring, the
per-file processing loop, datapackage writing, and dry-run planning all live on one
class — and `CommonProcessor` reaches back into it (`project.project`,
`project.project_path`, `project.output`, `project.state` at
`processors/base.py:255-324`), so the processor cannot be tested or reused without a
full Project. Phase 3 of the 2026-10 improvement roadmap.

## What Changes
- Extract config loading/interpolation into a small loader (e.g.
  `common/projectconfig.py`) returning a typed config object; `Project` consumes it.
- Extract logging setup (already consolidated by the error-handling change) out of
  `Project`.
- Introduce a `ProcessorConfig` dataclass; `CommonProcessor` accepts it (plus explicit
  paths/state) instead of the whole `Project` — feature envy removed.
- Keep `Project` as the CLI-facing orchestrator: stage wiring, run/status/clean
  behavior, and exit semantics unchanged.
- No CLI behavior, config format, or state-file changes.

## Impact
- Affected specs: `processors`
- Affected code: `datacrafter/cmds/project.py`, `datacrafter/processors/base.py`,
  possibly `datacrafter/common/state.py`
- Depends on: `improve-error-handling-and-typing` (logging owner) for a clean seam;
  benefits from `complete-registry-factories` slimming the wiring.
