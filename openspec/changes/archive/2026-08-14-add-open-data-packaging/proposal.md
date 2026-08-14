# Change: Open-data packaging (Frictionless, Parquet, env secrets, catalogs, multi-extractor)

## Why
The remaining niche-depth gap is packaging and catalog ingestion: secrets sit in
YAML, there is no Parquet or Data Package output, RSS/DCAT catalogs cannot be
walked, and a project can declare only one extractor.

## What Changes
- Interpolate `${VAR}` and `${VAR:-default}` in `datacrafter.yml` after `safe_load`.
- Write `datapackage.json` next to file destinations (Table Schema from inferred types).
- Register optional `file-parquet` destination (pyarrow).
- Add `rss` and `dcat` extractor types (feed/catalog → JSONL, optional file download).
- Accept `extractors:` as a list sharing one processor and destination.

## Impact
- Affected specs: `data-collection`, `source-dest-registry`, `config-validation`, `data-package`, `catalog-extract`
- Affected code: `load_config`, destinations, extractors, `Project.collect`/`finish`, validation, examples
- Risk: medium. Singular `extractor:` remains the default; parquet and pyarrow stay optional.
