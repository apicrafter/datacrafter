## Context
`autoid` / `autotype` are already keys in `DEFAULT_CONFIG_PARAMS` but never applied.
`schema` / `metrics` CLI commands echo “not yet”. There is no dry-run. `examples/`
points at an external repo except for one DCAT YAML.

## Goals / Non-Goals
- Goals: make those config/CLI claims true with tests; keep YAML backward compatible.
- Non-Goals: Frictionless/Parquet, UI, builds/push, multi-resource YAML, env-var secrets (Phase 4).

## Decisions
- **Autoid is opt-in** (`default: false`). The old unused default was `true`; applying that would add `_id` to every pipeline that never set the flag.
- **Autotype samples first N records** (default 100) after keymap-only projection so inferred names match explicit `typemap` keys. Remaining records are processed in the same pass via `itertools.chain`.
- **Explicit typemap wins** over inferred types. Inferred `string` is omitted (no conversion).
- **Autoid last** in the pipeline so custom scripts can populate key fields. Existing `_id` is left unchanged.
- **Dry-run** validates, prints extractor/processor/destination and an estimate from files already in `current/`, and does not download or write.
- **schema/metrics** read uncompressed `.jsonl` in `output/` first, then `current/`. Compressed files are out of scope for this change.

## Risks / Trade-offs
- Sampling can miss rare types → Mitigation: `typemap` override; document sample size.
- Sidecar grows on skip-heavy jobs → Mitigation: append-only JSONL next to output; counts in `state.json`.

## Migration Plan
No YAML schema break. Users enable autotype/autoid explicitly. `datacrafter schema` / `metrics` / `run --dry-run` are new surfaces.
