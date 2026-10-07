## MODIFIED Requirements
### Requirement: Maintained CI Actions and Python Matrix
CI workflows SHALL use currently-supported GitHub Actions versions (no EOL or
deprecated-runtime major versions, including `actions/stale` and the code-coverage
upload action) and SHALL test against supported Python versions only, consistently
across workflows.

#### Scenario: no EOL actions or Pythons
- **WHEN** the workflow files are inspected
- **THEN** they use `actions/checkout@v4+`, `actions/setup-python@v5+`,
`github/codeql-action@v3+`, current majors of stale/codecov actions, and test against
Python 3.10 through 3.13 (no EOL 3.9)
