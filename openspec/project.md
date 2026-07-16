# Project Context

## Purpose
Datacrafter is an open-source NoSQL-first ETL (Extract, Transform, Load) command-line
tool. It builds data pipelines that extract data from APIs/files/web sources, transform
it with type detection and key mapping, and load it into file formats (JSONL/BSON/CSV)
or databases (MongoDB, ArangoDB, CouchDB, Meilisearch). Currently in alpha stage.

## Tech Stack
- **Language:** Python 3.8+ (targeting modernization to 3.10+)
- **CLI framework:** Typer
- **Data formats:** orjson, jsonlines, pymongo (BSON), openpyxl, xlrd, lxml
- **Networking:** requests, beautifulsoup4
- **Config:** PyYAML (`datacrafter.yml`)
- **Packaging:** setuptools via `setup.py` (legacy; migrating to `pyproject.toml`)
- **Testing:** pytest, pytest-cov, pytest-mock, pytest-httpbin

## Project Conventions

### Code Style
- Line length: 88 (Black-compatible; configured in `.pylintrc`)
- Logging over `print()` — no `print()` calls in `datacrafter/` package code
- Optional dependencies guarded with `try/except ImportError` + `HAS_*` flags
- Snake_case for functions/variables; UPPER_CASE for constants

### Architecture Patterns
- ETL pipeline: Extract (extractors) → Process (processors) → Load (destinations)
- Abstract base classes define protocols in `sources/base.py`, `destinations/base.py`
- Factory functions in `sources/__init__.py` and `destinations/__init__.py` dispatch
  on config `type` via if/elif chains (planned migration to plugin registry)
- `Project` (`cmds/project.py`) orchestrates the pipeline; `core.py` is the Typer CLI
- State persisted via `common/state.py:ProjectState`

### Testing Strategy
- pytest with coverage; target 80% (currently ~35%, unenforced)
- Tests in `tests/`; `--strict-markers` enabled; markers: unit/integration/slow/backend
- External services (Mongo/Arango/CouchDB/Meilisearch) must be mocked, not hit live

### Git Workflow
- `main` branch; feature branches named `fix/*` or `feat/*`
- Version single-sourced in `datacrafter/__init__.py:__version__`
- CHANGELOG.md follows Keep a Changelog + SemVer

## Domain Context
- NoSQL-first: JSON Lines and BSON are the native intermediate formats
- Config-driven: pipelines defined declaratively in `datacrafter.yml`
- Threat model: config files and `code`-type extractor scripts are trusted (runpy is
  intentional), but URLs/filenames flowing into shell commands are NOT trusted

## Important Constraints
- Apache License 2.0 (NOT BSD — classifier must be corrected)
- Backward compatibility with existing `datacrafter.yml` configs must be preserved
- Optional deps (pymongo, python-arango, meilisearch, pycouchdb) must stay optional

## External Dependencies
- Optional DB drivers: pymongo (MongoDB), python-arango (ArangoDB),
  meilisearch (Meilisearch), pycouchdb (CouchDB) — guarded by try/except imports
- apibackuper (unpinned — external tool for API backups)
