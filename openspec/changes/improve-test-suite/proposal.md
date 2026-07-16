# Change: Improve Test Suite Coverage & Quality

## Why
Coverage is 35% against an 80% target. Critical surfaces are untested: all four DB
backends (Mongo/Arango/CouchDB/Meilisearch) at 0–31%, `core.py` (533-line CLI) at 0%,
`common/collect.py` (all HTTP code) at 18.8%, `extractors/base.py run()` unhit. There
is **zero mocking** despite `pytest-mock`/`pytest-httpbin` being declared. Two files
(`test_real_usage.py`, `test_tqdm_fallback.py`) are scripts using `print()`+`sys.exit`
instead of pytest assertions. Three compression test files heavily overlap. Coverage
config is duplicated in both `.coveragerc` and `pytest.ini`. Custom markers
(`integration`, `backend`) are declared but unused.

## What Changes
- Add mock-based tests for each DB destination (mock the driver clients).
- Add tests for `common/collect.py` using `pytest-httpbin`/`requests_mock` patterns
  and mocked aria2 subprocess.
- Add CLI tests for `core.py` commands via `typer.testing.CliRunner`.
- Convert `test_real_usage.py` and `test_tqdm_fallback.py` to real pytest tests.
- Deduplicate the three compression test files into one.
- Remove the duplicate `[coverage:*]` block from `pytest.ini` (keep `.coveragerc`).
- Apply the `@pytest.mark.integration` / `@pytest.mark.backend` markers consistently.

## Impact
- Affected specs: `testing`
- Affected code: `tests/*`, `pytest.ini`, `.coveragerc`
- Risk: low; test-only changes. Goal: lift coverage from 35% → 60%+ as a first ratchet.
