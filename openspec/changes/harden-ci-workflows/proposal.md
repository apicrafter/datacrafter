# Change: Harden CI workflows

## Why
The October 2026 CI review found: no concurrency groups on `tests.yml`/`pylint.yml`/
`publish.yml` (pylint triggers on every branch push *plus* PRs, doubling every run);
the pip-audit job audits only the version floors in `requirements.txt`, never the
resolved environment, dev requirements, or pins, and there is no Dependabot config;
the pylint job has no pip caching and omits Python 3.13; `actions/stale@v5` runs on a
deprecated node16 runtime and `codecov-action@v4` is deprecated; releases are
PyPI-only with no GitHub Release; and there is no CODEOWNERS. Phase 2 of the 2026-10
improvement roadmap.

## What Changes
- Add `concurrency: { group: <workflow>-<ref>, cancel-in-progress: true }` to
  `tests.yml`, `pylint.yml`, `publish.yml`; restrict `pylint.yml` triggers to PRs
  against `main` (and pushes to `main`).
- Pylint job: reuse the `requirements-dev.txt` pins (landing with the pending working
  tree change), add pip caching, add Python 3.13 to the matrix.
- Scanning: weekly scheduled `pip-audit` against the fully resolved environment
  (`pip install -r requirements-dev.txt && pip-audit`), plus Dependabot config for
  `pip`, `github-actions`, and npm (`docs/`).
- Bump `actions/stale` to the current major (v9) and `codecov-action` to v5.
- Add a GitHub Release step to `publish.yml` (tag → release notes from CHANGELOG,
  e.g. via `softprops/action-gh-release`), attaching wheel/sdist artifacts.
- Add a minimal `CODEOWNERS`.

## Impact
- Affected specs: `continuous-integration`
- Affected code: `.github/workflows/{tests,pylint,publish,stale}.yml`,
  new `.github/dependabot.yml`, new `.github/CODEOWNERS`
- Prerequisite: commit the pending pylint/pins working-tree change-set first (it is
  the basis for the pylint matrix pins).
