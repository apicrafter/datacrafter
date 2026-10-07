# Change: Unify logging ownership, exception hierarchy, and write-failure handling

## Why
The October 2026 analysis found logging configured by three competing owners
(`__main__.py:13` sets WARNING, importing `core` resets the root logger to INFO at
import time in `core.py:21`, then `Project.enable_logging` reconfigures again and
clears handlers a library user may have installed); six exception families sharing no
root (`ProcessingError`, `DataCrafterConfigurationError`, `MissingEnvVarError`,
`Unknown*TypeError(KeyError)`); and write/close failures downgraded to warnings in
nested broad-except clusters (`destinations/base.py:152-201`,
`cmds/project.py:288-305`), so failed loads can end as "successful" runs. Typing
covers only 17% of functions and mypy is configured for 3 files. Phase 2 of the
2026-10 improvement roadmap.

## What Changes
- Single logging owner: remove the import-time `configure_logging` call from
  `core.py`; `__main__` and the CLI own level/handlers once; `Project.enable_logging`
  adds its file handler without clearing existing root handlers.
- Introduce a `DataCrafterError` base exception; re-parent
  `ProcessingError`/`RecordProcessingError`, `DataCrafterConfigurationError`,
  `MissingEnvVarError`, and the `Unknown*TypeError` family onto it (the Unknown types
  leave `KeyError` to avoid quoted-message rendering).
- Let destination write/flush/close errors propagate to `Project.run` and fail the
  stage and exit code; keep best-effort narrow catches only for cleanup of already-
  failed resources; record the error in `state.json`.
- Reduce per-record log noise (single WARN per skipped record; demote per-value
  conversion INFO logs to DEBUG).
- Gradual typing: mypy over the whole `datacrafter` package (start non-strict, gate in
  CI), annotate the `Base*` ABC signatures and `common/` first.

## Impact
- Affected specs: `code-quality`
- Affected code: `datacrafter/core.py`, `datacrafter/__main__.py`,
  `datacrafter/common/logconfig.py`, `datacrafter/cmds/project.py`,
  `datacrafter/destinations/base.py`, `datacrafter/processors/base.py`,
  `datacrafter/extractors/base.py`, `datacrafter/common/env.py`,
  `datacrafter/_registry.py`, `pyproject.toml` (mypy files list)
