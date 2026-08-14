## 1. Config and secrets
- [x] 1.1 Interpolate `${VAR}` / `${VAR:-default}` after YAML safe_load
- [x] 1.2 Fail load when a required `${VAR}` is unset
- [x] 1.3 Accept `extractors:` list in validation (singular `extractor` still valid)

## 2. Destinations and packaging
- [x] 2.1 Register `file-parquet` destination (optional pyarrow)
- [x] 2.2 Write `datapackage.json` beside file output unless disabled

## 3. Catalog extractors
- [x] 3.1 RSS/Atom extractor → JSONL (optional enclosure download)
- [x] 3.2 DCAT catalog extractor → JSONL (optional distribution download)
- [x] 3.3 `Project.collect` runs every extractor in `extractors:`

## 4. Verification
- [x] 4.1 Tests for env, parquet (skip if no pyarrow), datapackage, rss/dcat parse, extractors list
- [x] 4.2 Docs/examples; `openspec validate add-open-data-packaging --strict`
