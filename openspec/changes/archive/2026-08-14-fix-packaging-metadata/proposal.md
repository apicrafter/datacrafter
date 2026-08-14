# Change: Fix Packaging Metadata & Modernize Build

## Why
The project uses legacy `setup.py` packaging with several metadata defects: the PyPI
license classifier declares **BSD** but the LICENSE file is **Apache 2.0**; the
`extras_require` key is a nonsensical duplicate condition
(`python_version == "3.8" or python_version == "3.8"`) producing junk
`Provides-Extra` metadata; `tests_require`/`cmdclass={'test': PyTest}` rely on
`python setup.py test` which was removed in setuptools 72.0; Python classifiers only
list 3.8 (EOL Oct 2024) despite `python_requires='>=3.8'`. There is no PEP 517/518
build-system declaration.

## What Changes
- Correct the license classifier from `BSD License` to `Apache Software License`.
- Remove the duplicate `extras_require` condition (argparse is built-in on all
  supported Pythons; the conditional is obsolete).
- Remove `tests_require` and `cmdclass={'test': PyTest}` (dead on modern setuptools).
- Add classifiers for Python 3.9–3.13; drop EOL 3.8 from the tested matrix.
- **Migrate to `pyproject.toml`** with PEP 621 metadata and a PEP 517 build-system,
  keeping `setup.py` as a thin shim (or removing it) — single source of truth.
- Keep version single-sourced in `datacrafter/__init__.py:__version__` and read it
  via `dynamic = ["version"]` + `tool.setuptools.dynamic`.

## Impact
- Affected specs: `packaging`
- Affected code: `setup.py`, new `pyproject.toml`, `setup.cfg` cleanup
- Risk: medium — packaging changes affect how the wheel/sdist is built; must verify
  `pip install -e .` and `python -m build` both succeed.
