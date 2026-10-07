## ADDED Requirements
### Requirement: Single Style-Lint Configuration Owner
Style linting SHALL be owned by exactly one tool configuration (ruff in
`pyproject.toml`); no duplicate or conflicting legacy lint configuration files (e.g. a
root `flake8` file and a `[flake8]` section in `setup.cfg`) SHALL remain in the
repository.

#### Scenario: no conflicting lint configs
- **WHEN** the repository root is inspected for lint configuration
- **THEN** style rules are defined only in `pyproject.toml` under `[tool.ruff]`

### Requirement: No IDE or Scratch Artifacts Tracked
The repository SHALL NOT track IDE state (`.idea/`) or personal scratch documents;
durable working notes live under versioned documentation directories instead.

#### Scenario: clean tracked file list
- **WHEN** `git ls-files` is inspected
- **THEN** it contains no `.idea/` entries and no superseded scratch notes
