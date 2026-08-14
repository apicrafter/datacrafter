# Project Context

## Purpose
Datacrafter is an open-source NoSQL-first ETL (Extract, Transform, Load) command-line
tool. It builds data pipelines that extract data from APIs/files/web sources, transform
it with type detection and key mapping, and load it into file formats (JSONL/BSON/CSV)
or databases (MongoDB, ArangoDB, CouchDB, Meilisearch). Currently in alpha stage.

## Tech Stack
- **Language:** Python 3.9+ (CI matrix 3.9–3.13)
- **CLI framework:** Typer
- **Data formats:** orjson, jsonlines, pymongo (BSON), openpyxl, xlrd, lxml
- **Networking:** requests, beautifulsoup4
- **Config:** PyYAML (`datacrafter.yml`)
- **Packaging:** PEP 621 `pyproject.toml` (setuptools); `setup.py` is a shim
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
- Factory functions in `sources/__init__.py`, `destinations/__init__.py`, and
  `extractors/__init__.py` validate `type` via the decorator registry in
  `_registry.py`, then construct instances (per-type kwargs still live in the
  source/destination factories)
- `validate_config` / `check_environment` live in `common/validation.py`;
  `Project.validate()` and the CLI `check` / `config validate` commands share them
- `Project` (`cmds/project.py`) orchestrates the pipeline; `core.py` is the Typer CLI
- State persisted via `common/state.py:ProjectState`

### Testing Strategy
- pytest with coverage; floor `fail_under = 80` in `.coveragerc`
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
- Apache License 2.0
- Backward compatibility with existing `datacrafter.yml` configs must be preserved
- Optional deps (pymongo, python-arango, meilisearch, pycouchdb) must stay optional

## External Dependencies
- Optional DB drivers: pymongo (MongoDB), python-arango (ArangoDB),
  meilisearch (Meilisearch), pycouchdb (CouchDB) — guarded by try/except imports
- apibackuper (>=1.0.4) — external tool for API backups
