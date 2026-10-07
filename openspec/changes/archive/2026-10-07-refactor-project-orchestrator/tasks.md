## 1. Implementation
- [x] 1.1 Extract config load/validate/interpolate into a loader module returning a
  typed config object; `Project.__init__` consumes it (keep `load_config` behavior and
  its docstring rationale)
- [x] 1.2 Move `JSONFormatter` and logging enablement out of `Project` to the logging
  owner module
- [x] 1.3 Define `ProcessorConfig` (autotype, autoid, autoid_fields, error strategy,
  keymap, typemap, buffer size, custom code path) as a dataclass with defaults
  matching current `DEFAULT_CONFIG_PARAMS`
- [x] 1.4 Change `CommonProcessor` to take `ProcessorConfig` + explicit
  output/state/errors paths; remove `project.*` attribute access
- [x] 1.5 Update `Project` call sites and dry-run plan construction
- [x] 1.6 Split `Project.process` (72 lines, 4 nesting levels) into per-resource
  helpers (setup/transform/write/close)

## 2. Tests
- [x] 2.1 Existing project/processor/CLI tests pass unchanged (behavior gate)
- [x] 2.2 New test: `CommonProcessor` runs with only `ProcessorConfig` + paths (no
  `Project` instance constructed)
- [x] 2.3 New test: config loader applies env interpolation and reports the same
  errors as before
