## ADDED Requirements

### Requirement: Automated Test Execution in CI
CI SHALL run the full pytest test suite on every push and pull request against a
matrix of supported Python versions, and the build MUST fail when tests fail.

#### Scenario: tests run on push
- **WHEN** a commit is pushed to any branch or a pull request is opened
- **THEN** CI runs `pytest` against Python 3.10, 3.11, 3.12, and 3.13 and fails the build if any test fails

### Requirement: Coverage Gate
CI SHALL measure test coverage and enforce a minimum coverage threshold via
`fail_under`, preventing coverage from regressing below the configured floor.

#### Scenario: coverage below floor fails build
- **WHEN** a change reduces total coverage below the configured `fail_under` threshold
- **THEN** the CI build fails

### Requirement: Dependency Vulnerability Scanning in CI
CI SHALL run `pip-audit` (or equivalent) against the resolved dependencies and surface
known vulnerabilities, failing or warning the build per policy.

#### Scenario: vulnerable dependency detected
- **WHEN** a dependency with a known CVE is introduced
- **THEN** the pip-audit CI step reports it

### Requirement: Automated PyPI Publishing
CI SHALL publish the package to PyPI automatically when a release tag is created,
using Trusted Publishing (OIDC) rather than long-lived API tokens.

#### Scenario: tag triggers publish
- **WHEN** a version tag (e.g. `v1.0.5`) is pushed
- **THEN** CI builds the wheel and sdist and publishes to PyPI via Trusted Publishing

### Requirement: Maintained CI Actions and Python Matrix
CI workflows SHALL use currently-supported GitHub Actions versions (no EOL major
versions) and SHALL test against supported Python versions only.

#### Scenario: no EOL actions or Pythons
- **WHEN** the workflow files are inspected
- **THEN** they use `actions/checkout@v4+`, `actions/setup-python@v5+`, `github/codeql-action@v3+`, and test against Python 3.10 through 3.13 (no EOL 3.8)
