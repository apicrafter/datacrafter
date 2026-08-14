# dependencies Specification

## Purpose
CVE-free lower bounds for runtime dependencies, compatible with Python 3.11+.
## Requirements
### Requirement: Dependency Versions Free of Known Vulnerabilities
All declared runtime dependencies SHALL use versions at or above the fixed releases
for known CVEs, and pinned production versions MUST pass `pip-audit` with no known
vulnerabilities.

#### Scenario: pip-audit clean
- **WHEN** `pip-audit` is run against the resolved dependency set
- **THEN** it reports zero known vulnerabilities

### Requirement: All Dependencies Pinned with Lower Bounds
Every direct dependency declared in `requirements.txt` and the packaging metadata MUST specify a minimum version bound, including previously unpinned packages (e.g. `apibackuper`).

#### Scenario: no unpinned dependencies
- **WHEN** the dependency declarations are inspected
- **THEN** every entry has a `>=` lower bound (no bare package names without versions)

### Requirement: Python 3.11+ Compatible Dependencies
The dependency set SHALL be installable and functional on Python 3.11, 3.12, and
3.13, and MUST NOT pin versions (e.g. `pandas==1.1.3`) that are incompatible with
modern Python.

#### Scenario: install on Python 3.12
- **WHEN** dependencies are installed in a Python 3.12 environment
- **THEN** all packages resolve and import successfully

