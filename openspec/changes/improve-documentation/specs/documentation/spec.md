## ADDED Requirements

### Requirement: Contribution Guide
The repository SHALL include a `CONTRIBUTING.md` describing environment setup, how to
run tests and linters, branching/commit conventions, and the pull-request process.

#### Scenario: contributor onboarding
- **WHEN** a new contributor reads `CONTRIBUTING.md`
- **THEN** they find instructions to set up the project, run tests, and submit a PR

### Requirement: Security & Trust Model Documented
The README SHALL document the security trust model: configuration files and `code`-type
extractor scripts are treated as trusted, while URLs and filenames are untrusted and
must not flow into shell commands.

#### Scenario: trust model visible
- **WHEN** a user reads the README
- **THEN** a Security section explains what inputs are trusted and how to report vulnerabilities

## MODIFIED Requirements

### Requirement: Accurate Internal Documentation Links
The README SHALL contain only links to files that exist in the repository and MUST NOT
reference non-existent files (e.g. `IMPROVEMENTS.md`).

#### Scenario: no broken doc links
- **WHEN** the README's internal links are checked
- **THEN** every linked file exists in the repository

### Requirement: No Stale Repository Artifacts
The repository SHALL NOT contain stale backup files (e.g. `README.rst_`) or obsolete
build artifacts in `dist/`, and `docs/.gitignore` SHALL cover `node_modules/`.

#### Scenario: clean repo root
- **WHEN** the repository root is inspected
- **THEN** no `*.rst_` or stale `dist/*.egg` artifacts are present
