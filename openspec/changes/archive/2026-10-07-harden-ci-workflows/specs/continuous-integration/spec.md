## MODIFIED Requirements
### Requirement: Dependency Vulnerability Scanning in CI
CI SHALL run `pip-audit` (or equivalent) against the resolved dependency environment
(installed packages, including dev requirements) on pull requests, and SHALL
additionally run a scheduled scan at least weekly so newly-published CVEs in pinned
or floored versions surface without code changes. Known vulnerabilities fail or warn
the build per policy.

#### Scenario: vulnerable dependency detected
- **WHEN** a dependency with a known CVE is introduced
- **THEN** the pip-audit CI step reports it

#### Scenario: scheduled scan runs without activity
- **WHEN** a week passes with no commits
- **THEN** the scheduled audit job still runs and reports on the current resolution

### Requirement: Maintained CI Actions and Python Matrix
CI workflows SHALL use currently-supported GitHub Actions versions (no EOL or
deprecated-runtime major versions, including `actions/stale` and the code-coverage
upload action) and SHALL test against supported Python versions only, consistently
across workflows.

#### Scenario: no EOL actions or Pythons
- **WHEN** the workflow files are inspected
- **THEN** they use `actions/checkout@v4+`, `actions/setup-python@v5+`,
`github/codeql-action@v3+`, current majors of stale/codecov actions, and test against
Python 3.9 through 3.13 in every job that lints or tests the package

## ADDED Requirements
### Requirement: Workflow Concurrency Control
Test, lint, and publish workflows SHALL define concurrency groups keyed by workflow
and ref with cancel-in-progress for superseded runs, and lint workflows SHALL trigger
only for relevant refs (main and its pull requests) so a pull request does not queue
duplicate runs.

#### Scenario: superseded push is cancelled
- **WHEN** two pushes land on the same branch in quick succession
- **THEN** the first run is cancelled and only the latest completes

#### Scenario: pull request does not double-run lint
- **WHEN** a PR is opened from a branch that also triggers push events
- **THEN** the lint workflow runs once for the PR, not once per event

### Requirement: Release Artifacts Published to GitHub
When a version tag is published, CI SHALL create a GitHub Release with notes derived
from `CHANGELOG.md` for that version and attach the built wheel and sdist, in addition
to the PyPI upload.

#### Scenario: tag produces a GitHub Release
- **WHEN** a `v*` tag is pushed
- **THEN** a GitHub Release exists for that version with CHANGELOG-derived notes and
  the wheel/sdist attached
