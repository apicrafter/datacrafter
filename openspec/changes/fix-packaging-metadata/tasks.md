## 1. Implementation
- [ ] 1.1 Create `pyproject.toml` with PEP 621 metadata + `[build-system]` (setuptools, wheel)
- [ ] 1.2 Set `dynamic = ["version"]` and `[tool.setuptools.dynamic] version = {attr = "datacrafter.__version__"}`
- [ ] 1.3 Fix license classifier → `License :: OSI Approved :: Apache Software License`
- [ ] 1.4 Add classifiers for Python 3.9, 3.10, 3.11, 3.12, 3.13
- [ ] 1.5 Remove duplicate `extras_require` condition (drop argparse entirely)
- [ ] 1.6 Remove `tests_require` and `cmdclass={'test': PyTest}`
- [ ] 1.7 Reduce `setup.py` to a minimal shim or remove if pyproject.toml is complete
- [ ] 1.8 Reconcile `setup.cfg` (keep only `[flake8]` config; move metadata to pyproject)

## 2. Tests
- [ ] 2.1 Verify `pip install -e .` succeeds in clean venv
- [ ] 2.2 Verify `python -m build` produces wheel + sdist
- [ ] 2.3 Verify `datacrafter --version` reports 1.0.4 from installed package

## 3. Verification
- [ ] 3.1 `python -m build` (or `pip wheel .`) succeeds
- [ ] 3.2 `python -c "import datacrafter; print(datacrafter.__version__)"` works
- [ ] 3.3 `openspec validate fix-packaging-metadata --strict`
