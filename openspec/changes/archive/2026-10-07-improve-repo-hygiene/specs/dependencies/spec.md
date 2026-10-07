## ADDED Requirements
### Requirement: Pinned Requirements Are Reproducible or Absent
If a pinned requirements file exists, it SHALL be generated from an actual dependency
resolution of a tested environment (e.g. `pip freeze` output) and be referenced by a
documented workflow; a file that merely restates the version floors from
`requirements.txt` provides false reproducibility and MUST be removed.

#### Scenario: pinned file reflects a real resolution
- **WHEN** the pinned requirements file is inspected
- **THEN** its pins differ from the bare floors where the tested resolution chose
  newer versions, and `DEPENDENCIES.md` documents how it is regenerated
