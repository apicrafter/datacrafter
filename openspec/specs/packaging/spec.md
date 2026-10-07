# packaging Specification

## Purpose
PEP 621 packaging metadata, Apache 2.0 license classifier, and Python 3.9–3.13 classifiers.
## Requirements
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

### Requirement: Self-Contained Sdist
The source distribution SHALL include the files required to run the shipped test suite
against it — notably the `examples/` recipes used by `tests/test_recipes.py` — via an
explicit `MANIFEST.in`.

#### Scenario: sdist contains examples
- **WHEN** `python -m build` produces the sdist and its contents are listed
- **THEN** the `examples/` directory with its recipe files is present

#### Scenario: recipe tests run from sdist
- **WHEN** the sdist is installed in a scratch environment and the recipe tests run
- **THEN** they pass without access to the original repository checkout

