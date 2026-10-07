# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-10-07

### Breaking
- Python 3.9 support dropped: `requires-python` is now `>=3.10` (3.9 reached
  end-of-life in October 2025). Users on 3.9 should stay on the previous
  release or upgrade. This unblocks modern dev floors: pylint 4, pre-commit
  4.6+, pip-audit 2.10+, pytest 9 (interpreter markers removed).

### Added
- Docusaurus documentation site in `docs/` (Getting Started, Concepts, Use
  Cases, CLI Reference, Configuration), with a GitHub Pages workflow for
  `https://apicrafter.github.io/datacrafter/`.
- Extractors register with `@register_extractor`; `get_extractor()` and
  `config schema` use `list_extractors()`.
- Processor `run()` uses a single buffered write path and records processor stats
  in `state.json`.
- `autotype` infers int/float/bool/date types from a record sample; `autoid` writes
  a stable `_id` (opt-in). Failed/skipped records go to `output/errors.jsonl`.
- `datacrafter schema`, `datacrafter metrics`, and `datacrafter run --dry-run`.
- In-repo pipeline recipes under `examples/`.
- `${VAR}` / `${VAR:-default}` interpolation in `datacrafter.yml`.
- `file-parquet` destination (optional pyarrow), `datapackage.json` beside file output.
- RSS/Atom and DCAT catalog extractors; `extractors:` list in one project.
- CLI tests for `run` and `status`; extractor `run()` tests with mocked downloads.
- Tests for JSON/BSON/XML/XLSX/XLS/ZIPXML sources, API/DCAT extractors, and
  Project collect/process/run.
- ruff + pre-commit; publish workflow runs tests before uploading to PyPI.
- Common exception root `DataCrafterError`: every public package exception
  (processing, configuration, env-var, unknown-type, destination-write errors)
  can be caught with one type. Destination flush/close failures raise
  `DestinationWriteError` and fail the run (recorded in `state.json`) instead
  of being logged as warnings.
- Sources and destinations own their construction via `from_config()`
  classmethods; the factories are registry lookup + delegation, and each class
  declares its compression capability (`COMPRESSION_MODE`). New plugins need
  no factory edits.
- `ProcessorConfig` dataclass: `CommonProcessor` runs with just a config and
  explicit paths — no `Project` instance required (library-friendly).
- Config loading lives in `common/projectconfig.py` (safe load + env
  interpolation), reusable without the orchestrator.
- Download options in extractor config: `timeout`, `verify_tls`, `aria2`,
  `aria2path` (documented in `docs/docs/configuration/security.md`).
- `compression` extra (`pip install datacrafter[compression]`) for zst files.
- CI: mypy job over the whole package, weekly scheduled pip-audit of the
  resolved environment, Dependabot (pip/npm/actions), concurrency groups,
  GitHub Release with CHANGELOG notes and wheel/sdist attached on tags,
  CODEOWNERS; stale@v9 and codecov-action@v5.
- `MANIFEST.in`: the sdist now ships `examples/` and `tests/`, so recipe tests
  run from an sdist checkout.

### Changed
- Documentation site replaced Jekyll/GitLab Pages with Docusaurus, organized
  like undatum (Getting Started, Concepts, Use Cases, CLI, Configuration).
- Coverage floor raised from 40% to 80% (currently ~85%).
- Source, destination, and extractor factories construct classes from the plugin registry.
- CI ruff job runs the full E/F/W/I set from `pyproject.toml` (not pyflakes-only).
- README and docs describe implemented features only; Meltano/ELT copy removed
  from the concepts docs. Python requirement documented as 3.9+.
- `run --dry-run` lists every `extractors:` entry (and keeps `extractor` as the first spec).
- `datacrafter init DIRECTORY` creates that directory (same as `--path`); docs match live extractor/destination types.
- Logging has a single owner (`common/logconfig.py`): no module configures the
  root logger at import time, and project logging preserves handlers installed
  by the embedding application. Verbose/quiet flags go through one function.
- Date/datetime conversion and typemap schema lookups are cached per distinct
  value (bounded caches), removing the two long-standing hot-path FIXMEs;
  schema inference shares the same cache.
- `BaseExtractor.run()` is a template method (validate → reset → `_execute()` →
  commit); each extractor subclass owns its mode's logic in `_execute()`.
- Failed-record logging is one WARNING line per record (was 2–3 lines);
  per-value conversion failures log at DEBUG.
- Compression tests are one parametrized grid (format × key × codec); coverage
  flags moved from `pytest.ini` addopts into CI, so local `pytest` runs are
  fast and artifact-free.
- `SUPPORTED_COMPRESSION` is derived from the implemented codec handlers;
  unsupported codecs raise a clear `ValueError` naming the supported set.

### Fixed
- Dev extras install on Python 3.9 again (`pylint` 4.x needs 3.10+).
- Pylint CI lints `datacrafter/` (not tests) and fails on errors only.
- XLSX source factory no longer raises `NameError` for `start_line` when XLS was
  not opened first in the same process.
- `Project.validate()` no longer always returns success.
- Source factory no longer treats a `.zip` archive as stream compression, so
  `zipxml` sources open the ZIP path.
- XLSX sources and `xlsx_to_json` honor the selected sheet (`page` / `start_page`)
  instead of always using the active worksheet.
- `set_dict_value` applied dotted-key writes to only the first element of a
  list; it now updates every element and creates missing intermediate keys.
- Compressed non-JSONL sources (e.g. `data.csv.gz`) read the decompressed
  content instead of garbage, and the decompression stream is owned and closed
  by the source. Formats that need a real file (xls/xlsx/zipxml) reject
  compression with a clear error.
- `XMLSource` releases parsed elements while iterating (bounded memory on large
  files) and supports a second full iteration pass via `reset()`.
- Destination `__del__` closes every owned stream (file, wrapper, archive):
  a garbage-collected ZIP destination no longer leaves a corrupt archive;
  destinations are context managers; `close()` is idempotent.
- Constructing a file source with neither `filename` nor `stream` raises a
  clear `ValueError` instead of `AttributeError` later.
- `ZIPSourceWrapper.__iter__` no longer leaks the previously opened archive
  member.
- `autoid_fields` accepts both a comma-separated string and a list (normalized
  identically), and the normalized list is exposed on the processor.

### Removed
- Unused runtime dependencies never imported by the package: pandas, orjson,
  chardet, jsonlines, tabulate, validators, dictquery, qddate — the install
  footprint shrinks substantially. `zstandard` became an optional extra.
- Dead code: nine unused source `read_bulk()` implementations, the legacy
  `converters.py` conversion suite (only `etree_to_dict` remains), the
  `TqdmFallback` class (tqdm is a hard dependency), unused constants, and
  commented-out blocks.
- Tracked IDE state (`.idea/`), working notes (`notes/` — durable content moved
  to `docs/docs/development/code-quality.md`), the duplicate root `flake8`
  config, and the never-consumed `requirements-pinned.txt`.

### Documentation
- Docs site synchronized with the 2026-10 code changes: download options
  (`timeout`, `verify_tls`, `aria2`) and RSS/DCAT keys documented; compressed
  inputs and `autoid_fields` in the processor reference; destination
  write-failure semantics in `run`/troubleshooting; phantom `storage: local`
  key removed from examples; zst `compression` extra in installation;
  contributing page reflects the current CI gates (mypy, pylint errors-only,
  coverage via `--cov`); new Code quality page listed in the sidebar.
- README: coverage floor corrected to 80%, local/coverage test commands
  split, compressed-input feature noted.

### Security
- Filenames derived from untrusted RSS/Atom enclosures and DCAT `downloadURL`
  are sanitized (no `..`, `.`, backslash or path-separator names), blocking a
  one-level directory escape from `current/`.
- URLs are logged with query strings redacted at INFO and above (query
  parameters may carry API keys); full URLs appear only at DEBUG.

## [1.0.4] - 2025-12-09

### Fixed
- **Code Quality Improvements**: Comprehensive pylint-based code quality improvements
  - Fixed all critical errors (E): Import errors for optional dependencies (`xmltodict`, `apibackuper`)
  - Fixed all abstract method warnings (W0223): Implemented missing abstract methods in `BaseFileDestination` and `BaseFileSource`
  - Fixed all unused import/argument warnings (W0611, W0613): Removed unused imports and prefixed unused arguments with `_`
  - Fixed variable naming issues (C0103): Renamed short exception variables (`e` → `error`, `f` → `file_obj`, `r` → `record`)
  - Fixed line length violations (C0301): Reformatted long lines, function signatures, and dictionary/list definitions
  - Improved error handling: Better exception variable naming throughout the codebase
  - Code quality score improved from 6.42/10 to 9.12/10 (+42% improvement)
  - Total issues reduced from 677 to 171 (75% reduction)

### Changed
- Improved code maintainability and readability
- Better error messages with properly named exception variables
- Enhanced code consistency across the codebase

### Documentation
- Added code quality recommendations documentation (`notes/CODE_QUALITY_RECOMMENDATIONS.md`)
- Added code quality summary (`notes/CODE_QUALITY_SUMMARY.md`)

## [1.0.3] - 2024-12-19

### Added
- Comprehensive documentation updates
- Configuration validation command (`datacrafter config validate`)
- Configuration schema command (`datacrafter config schema`)
- Improved error handling and validation
- Support for structured JSON logging
- Quiet mode for reduced output
- Status command to check pipeline execution state
- Log command to view execution logs
- Check command for configuration and environment validation
- **Zstandard (zst) compression support** for sources and destinations
- Support for both `compress` and `compression` configuration keys for backward compatibility
- Compression examples and test coverage

### Fixed
- Dependency management: Synchronized dependencies between `setup.py` and `requirements.txt`
- Added missing `dictquery` dependency to requirements
- Created `requirements-pinned.txt` for production builds
- Created `DEPENDENCIES.md` documentation
- Improved logging configuration (default to INFO level)
- Better error messages with actionable suggestions
- Compression configuration now supports both `compress` and `compression` keys

### Changed
- Default logging level changed from DEBUG to INFO
- Improved CLI structure and organization
- Enhanced configuration validation
- Better error handling throughout the codebase

### Documentation
- Updated README.md with comprehensive installation and usage instructions
- Added command reference section
- Added configuration examples
- Created DEPENDENCIES.md for dependency management
- Improved project documentation structure
- Added compression examples demonstrating zst support

## [1.0.2] - 2022-05-15

### Added
- First public release on PyPI
- Updated GitHub code repository
