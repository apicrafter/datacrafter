## 1. Packaging metadata
- [x] 1.1 `requires-python = ">=3.10"`; remove the 3.9 classifier; ruff
  `target-version = "py310"`
- [x] 1.2 requirements-dev.txt: drop all `python_version` markers; floors to
  `pylint>=4.0.0`, `pre-commit>=4.6.2`, `pip-audit>=2.10.1`, `pytest>=9.1.1`

## 2. CI
- [x] 2.1 tests.yml and pylint.yml matrices: 3.10–3.13; remove the pylint
  marker comment and inline version pins

## 3. Docs
- [x] 3.1 README, docs installation/contributing, CONTRIBUTING.md,
  openspec/project.md: Python 3.10+
- [x] 3.2 CHANGELOG [Unreleased]: breaking-change note

## 4. Validation
- [x] 4.1 Local: pytest, ruff, mypy, pylint, openspec validate
- [x] 4.2 Push; CI green on the 3.10–3.13 matrix (commit 152dae0: Tests/Pylint/CodeQL success)
