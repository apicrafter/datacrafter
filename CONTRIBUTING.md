# Contributing to Datacrafter

Thanks for your interest in contributing! This guide covers setup, testing, linting,
and the pull-request process.

## Development Setup

```bash
git clone https://github.com/apicrafter/datacrafter.git
cd datacrafter

# Create a virtual environment (Python 3.9+ required)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install runtime + dev dependencies, and the package in editable mode
pip install -r requirements-dev.txt
pip install -e .
```

Runtime dependencies live in `requirements.txt`; the build reads them from there
via `pyproject.toml` (`tool.setuptools.dynamic`), so there is a single source of
truth. See [DEPENDENCIES.md](DEPENDENCIES.md) for the full strategy.

## Running Tests

```bash
# Full suite with coverage (enforces the fail_under floor in .coveragerc)
pytest

# A single file / marker
pytest tests/test_mappers.py
pytest -m unit
```

Test coverage is gated at a minimum floor (currently 80%). Changes that
reduce coverage below the floor will fail CI; please add or update tests with your
change. External services (MongoDB, ArangoDB, CouchDB, Meilisearch) are mocked —
**never** write a test that requires a live database.

## Linting & Type Checking

```bash
pylint datacrafter/
ruff check datacrafter tests
mypy datacrafter/_registry.py datacrafter/sources/base.py datacrafter/destinations/base.py
pip-audit -r requirements.txt
```

Install git hooks with `pre-commit install`. CI runs pytest (coverage floor 80%), ruff (E/F/W/I), and pip-audit.

## Git Workflow

1. **Branch** off `main`: use `feat/<topic>` for features, `fix/<topic>` for bug
   fixes, `docs/<topic>` for documentation.
2. **Commit** with clear messages. We follow Conventional Commits-style prefixes
   (`feat:`, `fix:`, `test:`, `docs:`, `ci:`, `refactor:`) but it is not enforced.
3. **Tests must pass** and coverage must not drop below the floor.
4. **Open a pull request** against `main`. CI must be green before merge.

The version is single-sourced in `datacrafter/__init__.py:__version__` and mirrored
in [CHANGELOG.md](CHANGELOG.md). Do not bump the version in a feature branch unless
coordinating a release.

## Packaging

```bash
python -m build       # wheel + sdist in dist/
```

Releases publish to PyPI automatically when a `v*` tag is pushed (Trusted Publishing /
OIDC — no API tokens required). See `.github/workflows/publish.yml`.

## Reporting Issues & Security

- Bugs and feature requests: [GitHub Issues](https://github.com/apicrafter/datacrafter/issues).
- **Security vulnerabilities**: do not open a public issue. Use
  [GitHub Security Advisories](https://github.com/apicrafter/datacrafter/security/advisories/new).
  See the README "Security" section for the trust model (config files and `code`-type
  extractor scripts are trusted; URLs are not).

## License

By contributing, you agree your contributions are licensed under the Apache License 2.0.
