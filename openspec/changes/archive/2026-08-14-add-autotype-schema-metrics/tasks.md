## 1. Processor behavior
- [x] 1.1 Add type-inference helper (sample records → field types)
- [x] 1.2 Apply autotype in `CommonProcessor.run()`; merge with explicit typemap
- [x] 1.3 Add AutoidStep (configured fields or canonical JSON hash); default autoid false
- [x] 1.4 Write skipped/failed records to `output/errors.jsonl` and record the path in processor state

## 2. CLI
- [x] 2.1 `datacrafter run --dry-run` prints a plan and does not extract or write
- [x] 2.2 `datacrafter schema` prints inferred field types from project JSONL
- [x] 2.3 `datacrafter metrics` prints counts, nulls, and top-value histograms

## 3. Recipes and docs
- [x] 3.1 Add in-repo example YAML (CSV URL, XLSX, ZIP+XML, APIBackuper, keep DCAT)
- [x] 3.2 Update README / getting-started so autoid, autotype, schema, metrics, dry-run are documented as implemented

## 4. Verification
- [x] 4.1 Tests for autotype, autoid, sidecar, dry-run, schema, metrics
- [x] 4.2 `pytest` green; `openspec validate add-autotype-schema-metrics --strict`
