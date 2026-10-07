## 1. Logging
- [x] 1.1 Delete the import-time `configure_logging(logging.INFO)` in `core.py:21`;
  move level selection into the CLI entry path only
- [x] 1.2 Make `Project.enable_logging` add the rotating file handler without clearing
  `rootLogger.handlers`; preserve an externally configured level when DEBUG was not
  requested
- [x] 1.3 Consolidate `logconfig.configure_logging`, `core.enable_verbose`, and the
  quiet-mode block into one function owning level + handlers

## 2. Exceptions
- [x] 2.1 Add `DataCrafterError` (e.g. in a new `datacrafter/errors.py`); re-parent
  `ProcessingError`, `RecordProcessingError`, `DataCrafterConfigurationError`,
  `MissingEnvVarError`
- [x] 2.2 Re-parent `UnknownSourceTypeError`/`UnknownDestinationTypeError`/
  `UnknownExtractorTypeError` from `KeyError` onto `DataCrafterError`
- [x] 2.3 Deduplicate the 2–3 log lines per failed record to a single WARNING;
  demote per-value conversion failures to DEBUG

## 3. Write-failure propagation
- [x] 3.1 Rework `BaseFileDestination.close()` nested excepts: flush errors raise
  `ProcessingError`/`DataCrafterError`; close of already-failed resources stays
  best-effort with a debug log
- [x] 3.2 `Project.run`/`process`: destination `write`/`finish`/`close` errors fail the
  stage, set exit code non-zero, and are recorded in `state.json` and the failed-files
  report
- [x] 3.3 Datapackage write failure at `cmds/project.py:374-379` propagates the same
  way

## 4. Typing
- [x] 4.1 Annotate `Base*` ABC method signatures and `common/` modules
- [x] 4.2 Widen `pyproject.toml` `[tool.mypy] files` to the whole package (non-strict
  first); fix reported errors
- [x] 4.3 Add a CI mypy job (allow it to gate once clean)

## 5. Tests
- [x] 5.1 Test: destination write failure ⇒ non-zero exit, stage failed in state.json,
  error text present in report
- [x] 5.2 Test: importing `datacrafter.core` does not change root logger level
- [x] 5.3 Test: `Project.enable_logging` preserves pre-existing handlers
- [x] 5.4 Test: every public custom exception is an instance of `DataCrafterError`
- [x] 5.5 Update existing tests that rely on swallowed close errors
