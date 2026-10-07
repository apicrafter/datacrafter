## ADDED Requirements
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
