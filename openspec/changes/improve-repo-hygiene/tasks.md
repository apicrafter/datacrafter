## 1. Implementation
- [x] 1.1 `git rm -r --cached .idea/` and add `.idea/` to `.gitignore`
- [x] 1.2 Delete root `flake8` file and the `[flake8]` section from `setup.cfg`;
  remove `setup.cfg` entirely if it becomes empty
- [x] 1.3 Move durable recommendations from `notes/` into
  `docs/docs/development/code-quality.md`; delete stale scratch notes; replace the
  `notes/` `.gitignore` `*.*` pattern with explicit filenames
- [x] 1.4 Decide `requirements-pinned.txt`: generate from `pip freeze` in a documented
  workflow (and consume it in CI) or delete it; sync `DEPENDENCIES.md`
- [x] 1.5 Add `MANIFEST.in` (`recursive-include examples *`) and verify
  `python -m build` produces an sdist containing the examples

## 2. Tests
- [x] 2.1 Recipe tests still pass from an sdist install (`pip install dist/*.tar.gz`
  in a scratch venv, run `pytest tests/test_recipes.py`)
- [x] 2.2 `ruff check datacrafter tests` passes with the old flake8 configs removed
- [x] 2.3 `git ls-files` shows no `.idea/`, `notes/` scratch, or duplicate flake8
  configuration entries
