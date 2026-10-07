# Change: Remove dead code and unused runtime dependencies

## Why
The October 2026 analysis identified a meaningful dead-weight layer shipping to every
user: all nine source `read_bulk()` implementations have zero production callers, the
legacy conversion suite in `common/converters.py:60-181` (including a function with a
`global n` counter) is test-only, and `requirements.txt` declares 8 dependencies the
package never imports — including pandas, the heaviest install in the set. Since
`pyproject.toml` sources runtime dependencies from `requirements.txt`, all of it ships.
Phase 2 of the 2026-10 improvement roadmap.

## What Changes
- Delete the unused source `read_bulk()` methods (`sources/csv.py:47`, `jsonl.py:28`,
  `json.py:32`, `xls.py:82`, `xlsx.py:63`, `xml.py:49`, `bsonf.py:37`, `zipped.py:59`)
  and the base default if it becomes orphaned.
- Delete the legacy conversion suite in `common/converters.py` and its dedicated test
  file; delete test-only helpers `get_dict_value_deep`, `update_dict_values`
  (`common/common.py`), `get_file_by_name` (`common/collect.py:177`).
- Delete unused constants (`DATE_PATTERNS`, `SUPPORTED_FILE_TYPES`, `DEFAULT_OPTIONS`,
  `DEFAULT_DICT_SHARE`), the `TqdmFallback` class (tqdm is a hard dependency), dead
  stdlib import guards, the unreachable `raise` at `sources/__init__.py:195-197`, the
  identical if/else branches at `sources/__init__.py:119-122`, commented-out code
  blocks (`mappers.py:56,72,93,203`, `sources/csv.py:29-30`, `couchdb.py:27`,
  `extractors/base.py:84-86`), and stray `pass` statements.
- Rewrite `SUPPORTED_COMPRESSION` (`destinations/base.py:16-21`) to be derived from the
  actual codec handler table, so membership reflects real capability.
- **BREAKING** (install footprint): remove `pandas`, `orjson`, `chardet`, `jsonlines`,
  `tabulate`, `validators`, `dictquery`, `qddate` from `requirements.txt`; move any
  that earn a use case to `[project.optional-dependencies]` extras.
- Declare the genuinely-optional `zstandard` as a `compression` extra and give its
  absence a friendly `ImportError` in `sources/__init__.py` (currently an unguarded
  `NameError`).
- Update `project.md` tech-stack notes and `DEPENDENCIES.md`.

## Impact
- Affected specs: `code-quality`, `dependencies`
- Affected code: `datacrafter/sources/*.py`, `datacrafter/common/converters.py`,
  `datacrafter/common/common.py`, `datacrafter/common/collect.py`,
  `datacrafter/constants.py`, `datacrafter/destinations/base.py`,
  `datacrafter/processors/base.py`, `requirements.txt`, `pyproject.toml`, `openspec/project.md`
- `datacrafter.yml` configs remain fully compatible; only the installed dependency
  set shrinks.
