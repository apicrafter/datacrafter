# Change: Improve repository hygiene

## Why
The October 2026 analysis found tracked IDE state (`.idea/`, 7 files), two conflicting
flake8 configurations (root `flake8` file with line length 100 vs `setup.cfg` with 88)
while ruff actually owns style, a `notes/` directory of stale working documents whose
`.gitignore` pattern `*.*` silently hides future files, a `requirements-pinned.txt`
that merely restates the version floors and is consumed by nothing, and an sdist that
omits `examples/` (so sdist users cannot run the recipe tests). Phase 1 of the 2026-10
improvement roadmap.

## What Changes
- Untrack `.idea/` and add it to `.gitignore`.
- Delete the root `flake8` file and the `[flake8]` section in `setup.cfg` (ruff in
  `pyproject.toml` is the single style-lint owner; `setup.cfg` then has no remaining
  content and can be removed if empty).
- Fold durable content from `notes/` (`CODE_QUALITY_RECOMMENDATIONS.md` and friends)
  into `docs/docs/development/`, delete scratch notes, and replace the `*.*`
  gitignore pattern with explicit entries.
- Make `requirements-pinned.txt` reproducible (generated from a real resolution) or
  delete it; update `DEPENDENCIES.md` accordingly.
- Add `MANIFEST.in` including `examples/` (and `docs/` metadata as needed) so the
  sdist is self-contained for tests.

## Impact
- Affected specs: `code-quality`, `dependencies`, `packaging`
- Affected code: `.gitignore`, `flake8`, `setup.cfg`, `notes/`, `docs/`,
  `requirements-pinned.txt`, `DEPENDENCIES.md`, `MANIFEST.in`
- No runtime code changes; `datacrafter.yml` configs unaffected.
