## ADDED Requirements
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
