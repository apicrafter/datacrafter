# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Changed
- Documentation site replaced Jekyll/GitLab Pages with Docusaurus, organized
  like undatum (Getting Started, Concepts, Use Cases, CLI, Configuration).
- Coverage floor raised from 40% to 80%.
- Source, destination, and extractor factories construct classes from the plugin registry.
- CI ruff job runs the full E/F/W/I set from `pyproject.toml` (not pyflakes-only).
- README and docs describe implemented features only; Meltano/ELT copy removed
  from the concepts docs. Python requirement documented as 3.9+.
- `run --dry-run` lists every `extractors:` entry (and keeps `extractor` as the first spec).
- `datacrafter init DIRECTORY` creates that directory (same as `--path`); docs match live extractor/destination types.

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
