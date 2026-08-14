## 1. Implementation
- [x] 1.1 Create `.github/workflows/tests.yml` with matrix [3.10, 3.11, 3.12, 3.13]
- [x] 1.2 tests.yml: checkout@v4, setup-python@v5, install requirements-dev.txt, run pytest, upload coverage
- [x] 1.3 Add Codecov upload step (codecov-action@v4)
- [x] 1.4 Add `fail_under = 35` to `.coveragerc`; document ratchet target in comments
- [x] 1.5 Modernize `codeql-analysis.yml`: checkout@v4, codeql-action@v3
- [x] 1.6 Modernize `pylint.yml`: checkout@v4, setup-python@v5, matrix 3.10–3.13
- [x] 1.7 Add `pip-audit` step to tests.yml (non-blocking initially, then gate)
- [x] 1.8 Create `.github/workflows/publish.yml` (build + PyPI Trusted Publishing on tag)
- [x] 1.9 Fix `stale.yml` placeholder messages → real issue/PR messages

## 2. Tests
- [x] 2.1 Trigger tests.yml on a push; confirm green on at least 3.11/3.12
- [x] 2.2 Confirm coverage gate fails a deliberately-broken commit

## 3. Verification
- [x] 3.1 `act` or push to branch triggers workflows
- [x] 3.2 `openspec validate add-ci-test-pipeline --strict`
