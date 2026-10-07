# Change: Drop Python 3.9 support

## Why
Python 3.9 reached end-of-life in October 2025 — a year ago. Keeping it has
already blocked four dependency updates (requests 2.33+, pytest 9, pre-commit
4.6+, pip-audit 2.10+ all require >=3.10) and forces interpreter-marker pins
in requirements-dev.txt plus a dedicated pylint pin in CI.

## What Changes
- **BREAKING**: `requires-python` becomes `>=3.10`; the 3.9 trove classifier
  is removed.
- CI matrices (tests, pylint) drop Python 3.9.
- Dev floors move to the versions that were blocked: `pylint>=4.0.0`,
  `pre-commit>=4.6.2`, `pip-audit>=2.10.1`, `pytest>=9.1.1`; all
  `python_version` markers in requirements-dev.txt are removed.
- Docs (README, installation, contributing, project.md) state Python 3.10+.

## Impact
- Affected specs: `packaging`, `continuous-integration`
- Affected code: `pyproject.toml`, `.github/workflows/{tests,pylint}.yml`,
  `requirements-dev.txt`, docs pages
- Users on Python 3.9 must stay on the previous release or upgrade the
  interpreter; `datacrafter.yml` configs are unaffected.
