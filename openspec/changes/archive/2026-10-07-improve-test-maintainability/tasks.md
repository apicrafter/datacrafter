## 1. Implementation
- [x] 1.1 Replace `tests/test_zstd_compression.py:5` bare import with
  `pytest.importorskip("zstandard")`
- [x] 1.2 Rewrite compression tests as one parametrized module:
  `@pytest.mark.parametrize("format,key,codec,ext", [...])` covering
  jsonl/bson/csv × gz/bz2/xz/zip/zst × `compress`/`compression` keys; delete the
  duplicated unittest variant
- [x] 1.3 Fix marker drift: apply `pytestmark = pytest.mark.unit` to pure-unit files or
  delete unused markers from `pytest.ini`; update `tests/README.md` to match
- [x] 1.4 Move `--cov*` and `log_file` out of `addopts` into the CI test job command
- [x] 1.5 Promote `_RecordingDestination` to `conftest.py`; delete the unused
  `empty_state` fixture; convert manual `mkdtemp` setups to `tmp_path`
- [x] 1.6 Decide and execute on `pytest-mock` / `pytest-httpbin`: remove from
  `requirements-dev.txt` or start using them
- [x] 1.7 Clean stale root artifacts (`.coverage`, `coverage.xml`, `htmlcov/`,
  `pytest.log`) and confirm they are gitignored

## 2. Tests
- [x] 2.1 Add `autoid_fields` test: `"a, b"` string and `["a"]` list configs produce
  the same `_id` derivation
- [x] 2.2 Add direct tests for `configure_logging` (level set, handler count)
- [x] 2.3 Add direct tests for source/destination base contracts (`is_flat`, default
  `write_bulk` batching, close idempotence)
- [x] 2.4 Verify suite passes from a clean virtualenv (no zstandard installed) without
  collection errors
