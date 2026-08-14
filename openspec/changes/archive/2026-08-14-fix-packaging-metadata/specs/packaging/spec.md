## ADDED Requirements

### Requirement: PEP 621 Build System
The project SHALL declare its build system and metadata in a `pyproject.toml` file
following PEP 517/518/621, including a `[build-system]` table and project metadata,
and MUST NOT rely solely on legacy `setup.py`-based configuration.

#### Scenario: build from source
- **WHEN** a contributor runs `python -m build` in the repository root
- **THEN** a wheel and sdist are produced successfully using the declared build backend

#### Scenario: editable install
- **WHEN** a contributor runs `pip install -e .` in a clean virtual environment
- **THEN** the `datacrafter` package is importable and the console script is installed

### Requirement: Accurate License Classification
The packaging metadata SHALL declare the license as Apache Software License 2.0 in
both the project metadata and the trove classifier, consistent with the `LICENSE`
file and `__licence__` attribute.

#### Scenario: classifier matches LICENSE file
- **WHEN** the built package metadata is inspected
- **THEN** the trove classifier is `License :: OSI Approved :: Apache Software License` and matches the Apache 2.0 LICENSE file

### Requirement: Supported Python Versions Accurately Declared
The packaging metadata SHALL declare classifiers for every supported Python version
(3.9 through 3.13) and MUST NOT advertise end-of-life versions as supported.

#### Scenario: modern Python classifiers present
- **WHEN** the package classifiers are inspected
- **THEN** classifiers for Python 3.9, 3.10, 3.11, 3.12, and 3.13 are present
