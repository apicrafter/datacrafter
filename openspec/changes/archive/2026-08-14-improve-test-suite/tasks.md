## 1. Implementation
- [x] 1.1 Add `tests/test_destinations_db.py`: mock-based tests for Mongo, Arango, CouchDB, Meilisearch destinations
- [x] 1.2 Add `tests/test_collect.py`: tests for get_file/get_file_by_pattern with mocked requests + subprocess
- [x] 1.3 Add `tests/test_cli.py`: CliRunner tests for core.py commands (run/init/status/check/config validate)
- [x] 1.4 Add `tests/test_extractors.py` cases for BaseExtractor.run() paths (mocked downloads)
- [x] 1.5 Convert `tests/test_real_usage.py` → proper pytest assertions (remove print/sys.exit)
- [x] 1.6 Convert `tests/test_tqdm_fallback.py` → proper pytest assertions
- [x] 1.7 Merge `test_compression_simple.py` + `test_compression_manual.py` into `test_compression_config.py`; delete dupes
- [x] 1.8 Remove duplicate `[coverage:run]/[coverage:report]` block from `pytest.ini` lines 36-53
- [x] 1.9 Apply `@pytest.mark.integration`/`@pytest.mark.backend` markers where appropriate

## 2. Verification
- [x] 2.1 `pytest --cov=datacrafter --cov-report=term-missing` shows ≥60% coverage
- [x] 2.2 No test files use `sys.exit` for assertions
- [x] 2.3 `pytest --co -q` collects cleanly with no warnings
- [x] 2.4 `openspec validate improve-test-suite --strict`
