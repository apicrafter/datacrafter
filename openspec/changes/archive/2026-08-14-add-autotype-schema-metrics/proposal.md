# Change: Apply autotype/autoid and ship schema, metrics, dry-run, recipes

## Why
README and CLI still treat autotype, autoid, `schema`, `metrics`, and dry-run as
reserved stubs. Those are the advertised differentiators for a YAML NoSQL ETL
tool; leaving them unimplemented keeps the product looking unfinished after the
quality-bar work.

## What Changes
- Apply `processor.config.autotype` by sampling records, inferring int/float/bool/date/datetime, and merging with explicit `typemap` (explicit wins).
- Apply `processor.config.autoid` by setting a stable `_id` from configured fields or a canonical JSON hash (opt-in; default false).
- Write skipped/failed records to `output/errors.jsonl`.
- Implement `datacrafter schema` and `datacrafter metrics` against project JSONL output (or `current/`).
- Add `datacrafter run --dry-run` that validates config, prints a plan, and writes nothing.
- Add in-repo recipe YAML under `examples/`.

## Impact
- Affected specs: `processors`, `inspect`, `documentation`
- Affected code: `processors/base.py`, `common/mappers.py`, `cmds/project.py`, `core.py`, `examples/`, README/docs
- Risk: medium. Autoid defaults to false so existing pipelines do not gain `_id` unless enabled. Autotype only runs when set true.
