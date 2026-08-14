## Context
Open-data users need secrets out of YAML, a Parquet off-ramp, a Data Package beside
JSONL, and catalog extractors that match urlbypattern/DCAT workflows. A project
today can declare only one `extractor`.

## Goals / Non-Goals
- Goals: env interpolation, datapackage.json, file-parquet, rss/dcat extractors, `extractors:` list.
- Non-Goals: full Frictionless Python runtime, Meltano taps, S3, nested per-resource destinations with independent processors as a first-class `resources:` DAG.

## Decisions
- **Env syntax** is `${VAR}` (required) and `${VAR:-default}` (optional). Unset required vars fail at load time. Interpolation runs after `yaml.safe_load` on string values only.
- **datapackage.json** is written for file destinations unless `destination.datapackage` is false. Schema types are inferred from the written JSONL/CSV when present; otherwise fields are omitted.
- **Parquet** is optional (`pyarrow`). Nested records are stored as Arrow structs via `from_pylist`.
- **RSS/DCAT** download the catalog with `get_file`, emit JSONL, and optionally fetch enclosures / `downloadURL`s. No new XML/HTTP libraries.
- **extractors:** is a list; each run appends extractor results. `extractor:` (singular) still works.

## Risks
- Missing env vars break `check`/`run` → clear error listing the variable name.
- pyarrow absent → ImportError with install hint, same pattern as Mongo/Arango.
