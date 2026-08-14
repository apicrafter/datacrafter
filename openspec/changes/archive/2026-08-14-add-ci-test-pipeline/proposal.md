# Change: Add CI Test Pipeline & Modernize Workflows

## Why
CI runs only CodeQL and Pylint — **there is no workflow that runs the test suite.**
Coverage is ~35% against an unenforced 80% target. CI actions are outdated
(`checkout@v3`, `setup-python@v3`, `codeql-action@v2` which is EOL). The Python matrix
tops out at 3.10 (3.8 is EOL). `pip-audit` is declared but never run. There is no
publish workflow. `stale.yml` has placeholder messages.

## What Changes
- Add `.github/workflows/tests.yml`: matrix Python 3.10/3.11/3.12/3.13, install
  deps, run `pytest`, upload coverage to Codecov.
- Add `fail_under` to coverage config (start at 35, document ratcheting plan).
- Modernize all workflow actions: `checkout@v4`, `setup-python@v5`,
  `codeql-action@v3`; bump pylint matrix to 3.10–3.13.
- Add a `pip-audit` job/step to CI.
- Add `.github/workflows/publish.yml`: build on tag, publish to PyPI via Trusted
  Publishing (OIDC).
- Fix `stale.yml` placeholder messages.

## Impact
- Affected specs: `continuous-integration`
- Affected code: `.github/workflows/*.yml`, `.coveragerc`/`pytest.ini`
- Risk: low; CI-only changes. No production code touched except coverage config.
