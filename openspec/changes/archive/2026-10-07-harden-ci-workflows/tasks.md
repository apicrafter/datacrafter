## 1. Workflow changes
- [x] 1.1 Add concurrency groups (cancel-in-progress) to `tests.yml`, `pylint.yml`,
  `publish.yml`; scope `pylint.yml` triggers to `main` + PRs targeting `main`
- [x] 1.2 Pylint job: install pylint from `requirements-dev.txt` markers, add pip
  caching, extend matrix to Python 3.13
- [x] 1.3 Add weekly scheduled pip-audit job auditing the resolved dev environment
  (not only floors); keep the existing PR-time floors audit
- [x] 1.4 Add `.github/dependabot.yml` (pip, github-actions, npm ecosystem in `docs/`)
- [x] 1.5 Bump `actions/stale` to v9 and `codecov-action` to v5 (with token if needed)
- [x] 1.6 Add GitHub Release step to `publish.yml`: extract notes from CHANGELOG.md
  for the tag, attach dist artifacts
- [x] 1.7 Add `.github/CODEOWNERS` (@apicrafter/datacrafter or the active maintainer)

## 2. Verification
- [x] 2.1 Verified on PR #117: a follow-up push to the PR branch cancelled the
  in-progress Tests/CodeQL runs via the concurrency groups: confirm single queued run per workflow with
  cancel-in-progress on a follow-up push
- [x] 2.2 Audit job confirmed green on `main` (pip-audit of the resolved
  environment ran in the Tests workflow, run 37607923913)
- [x] 2.3 Dry-run release notes generation against the existing `v1.0.4` tag content (verified locally: awk extracts the 1.0.4 section)
