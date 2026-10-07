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

### Requirement: Pinned Requirements Are Reproducible or Absent
If a pinned requirements file exists, it SHALL be generated from an actual dependency
resolution of a tested environment (e.g. `pip freeze` output) and be referenced by a
documented workflow; a file that merely restates the version floors from
`requirements.txt` provides false reproducibility and MUST be removed.

#### Scenario: pinned file reflects a real resolution
- **WHEN** the pinned requirements file is inspected
- **THEN** its pins differ from the bare floors where the tested resolution chose
  newer versions, and `DEPENDENCIES.md` documents how it is regenerated

### Requirement: Minimal Runtime Dependency Set
Every dependency declared in `requirements.txt` (and therefore shipped via
`pyproject.toml`) SHALL be imported by the package or required at runtime by a
declared feature; heavyweight packages that no code imports (e.g. pandas) MUST NOT be
installed for all users and belong in optional extras if a use case exists.

#### Scenario: declared dependency is imported
- **WHEN** each entry in `requirements.txt` is cross-referenced against package imports
- **THEN** each is imported by production code or documented as a required external tool

#### Scenario: clean install is lean
- **WHEN** the package is installed into a fresh environment
- **THEN** pandas and the other previously-unused packages are not pulled in

### Requirement: Optional Codecs Declared as Extras
Genuinely optional codecs and drivers SHALL be declared in
`[project.optional-dependencies]` extras, and their absence MUST produce a friendly
`ImportError` naming the extra to install, never a `NameError`.

#### Scenario: zst read without zstandard
- **WHEN** a `.zst` source or destination is requested and `zstandard` is not installed
- **THEN** the error names the `compression` extra and the package to install

