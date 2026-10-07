## 1. Design
- [x] 1.1 Finalize the `from_config` signature (filename/stream, options dict) and the
  shared option-validation helpers per design.md

## 2. Implementation
- [x] 2.1 Add `from_config` classmethods to all source classes (csv, json, jsonl, xml,
  zipxml, xls, xlsx, bson, zipped), each validating its own required options
- [x] 2.2 Add `from_config` classmethods to all destination classes (file-jsonl,
  file-bson, file-csv, file-parquet, mongodb, arangodb, couchdb, meilisearch)
- [x] 2.3 Rewrite `get_source_from_file` / `get_destination` to lookup + delegate;
  delete if/elif chains and dead raises
- [x] 2.4 Convert `BaseExtractor.run()` to a template method; move `_run_*` logic into
  the corresponding subclasses; delete the five duplicate `run()` bodies
- [x] 2.5 Verify `datacrafter config schema` lists identical types before/after

## 3. Tests
- [x] 3.1 Existing factory tests pass unchanged (behavior compatibility)
- [x] 3.2 Add a test: registering a new stub plugin type requires zero factory edits
  (construct via registry only)
- [x] 3.3 Extractor template-method test: each registered extractor type executes its
  mode's run path
