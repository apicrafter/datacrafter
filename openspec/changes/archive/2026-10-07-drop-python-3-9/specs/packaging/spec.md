## MODIFIED Requirements
### Requirement: Supported Python Versions Accurately Declared
The packaging metadata SHALL declare classifiers for every supported Python
version (3.10 through 3.13), set `requires-python` accordingly, and MUST NOT
advertise end-of-life versions (3.9 and older) as supported.

#### Scenario: modern Python classifiers present
- **WHEN** the package classifiers are inspected
- **THEN** classifiers for Python 3.10, 3.11, 3.12, and 3.13 are present and
  no 3.9 classifier remains

#### Scenario: requires-python floor
- **WHEN** the packaging metadata is inspected
- **THEN** `requires-python` is `>=3.10`
