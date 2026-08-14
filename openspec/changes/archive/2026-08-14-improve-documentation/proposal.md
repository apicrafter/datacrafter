# Change: Improve Documentation & Repository Hygiene

## Why
README references `IMPROVEMENTS.md` (doesn't exist — broken link). A stale
`README.rst_` (trailing underscore) is committed at root. There is no `CONTRIBUTING.md`
or `CODE_OF_CONDUCT.md`. `stale.yml` has placeholder messages. Stale `dist/*.egg`
(1.0.2 era) sit on disk. `docs/node_modules/` not in `docs/.gitignore`. The README
Development section could link to the new CI and contribution flow.

## What Changes
- Remove broken `IMPROVEMENTS.md` links from README (or create the file).
- Delete the stale `README.rst_` from the repo root.
- Add `CONTRIBUTING.md` (setup, test, lint, branch/commit conventions, PR process).
- Fix `stale.yml` placeholder messages with real issue/PR stale text.
- Clean stale `dist/*.egg` build artifacts from disk.
- Add `node_modules/` to `docs/.gitignore`.
- Add a "Security" section to README documenting the trust model (config files and
  `code`-type extractor scripts are trusted; URLs are not) and reporting policy.
- Update README Development section to reference `pyproject.toml`, the new CI, and
  `pip-audit`.

## Impact
- Affected specs: `documentation`
- Affected code: `README.md`, `CONTRIBUTING.md` (new), `.github/workflows/stale.yml`,
  `docs/.gitignore`, `dist/` cleanup
- Risk: none (docs only).
