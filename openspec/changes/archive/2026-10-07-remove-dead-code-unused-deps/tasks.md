## 1. Dead code removal
- [x] 1.1 Delete all uncalled source `read_bulk()` implementations and orphaned base
  default
- [x] 1.2 Delete `common/converters.py` legacy suite (keep any function still imported
  in production — verify by grep) and `tests/test_converters.py`
- [x] 1.3 Delete test-only helpers: `get_dict_value_deep`, `update_dict_values`,
  `get_file_by_name`; migrate any genuinely useful assertion to use public paths
- [x] 1.4 Delete unused constants and `TqdmFallback`; remove tqdm fallback test
- [x] 1.5 Remove dead guards/branches/commented-out code listed in the proposal;
  derive `SUPPORTED_COMPRESSION` from the handler table

## 2. Dependency changes
- [x] 2.1 Verify each of the 8 unused deps by import-grep; remove from
  `requirements.txt` (move to extras only if a use exists)
- [x] 2.2 Add `compression = ["zstandard>=0.18"]` extra; guard the zstandard import
  with a friendly ImportError in `sources/__init__.py`
- [x] 2.3 Update `DEPENDENCIES.md` and `openspec/project.md` tech-stack lines
  (orjson/jsonlines references)
- [x] 2.4 Confirm CI matrix installs cleanly without the removed packages and
  `pip-audit` still passes

## 3. Tests
- [x] 3.1 Full suite green; coverage floor (80%) still met after deleting
  dead-code-covering tests
- [x] 3.2 Test that a zst file without zstandard installed raises the friendly
  ImportError (skipif-guarded)
- [x] 3.3 Test that `list_destinations()`/compression handling reflects the derived
  capability table (no phantom `7z`/`lz4`)
