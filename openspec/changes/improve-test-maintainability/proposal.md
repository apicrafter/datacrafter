# Change: Improve test suite maintainability and hermetic collection

## Why
The October 2026 test-suite review found one collection-breakage risk
(`tests/test_zstd_compression.py:5` does a bare module-level `import zstandard`, which
is in no requirements file — a fresh CI install fails to collect the file), zero use of
`pytest.mark.parametrize` across 254 tests while the compression suite alone contains
~11 copy-pasted variants, dead marker configuration documented as usable in
`tests/README.md`, and `--cov`/HTML/`pytest.log` output hardwired into `addopts` so
every local run regenerates four artifact trees in the repo root. Phase 1 of the
2026-10 improvement roadmap.

## What Changes
- Replace the bare `import zstandard` with `pytest.importorskip("zstandard")`.
- Collapse `test_compression_config.py` and `test_zstd_compression.py` into one
  parametrized module over `(format, key, codec, extension)`; convert unittest classes
  to pytest style.
- Reconcile markers with reality: either apply `pytestmark = pytest.mark.unit` per file
  or remove the unused `unit`/`slow`/`meta`/`concurrent` markers; fix `tests/README.md`.
- Move `--cov*` flags and the log file out of default `addopts` into the CI job; local
  `pytest` stays fast and artifact-free.
- Promote the duplicated `_RecordingDestination` to `conftest.py`; drop the unused
  `empty_state` fixture; standardize temp dirs on `tmp_path`.
- Remove unused `pytest-mock` / `pytest-httpbin` from `requirements-dev.txt` (or adopt
  them — decide once).
- Add a test for `autoid_fields` accepted as both comma string and list (covers the
  uncommitted `processors/base.py` change); add small direct tests for
  `common/logconfig.py` and the source/destination base contracts.

## Impact
- Affected specs: `testing`
- Affected code: `tests/` (zstd/compression test modules, `conftest.py`,
  `test_processors.py`, `test_real_usage.py`), `pytest.ini`, `requirements-dev.txt`,
  `tests/README.md`, `.github/workflows/tests.yml` (coverage flags)
