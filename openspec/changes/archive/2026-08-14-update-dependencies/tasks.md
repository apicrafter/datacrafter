## 1. Implementation
- [x] 1.1 Bump floors in `requirements.txt`: pymongo>=4.6, requests>=2.31, lxml>=4.9.1, pandas>=2.0, chardet>=5.0, beautifulsoup4>=4.12, pyyaml>=6.0.1
- [x] 1.2 Mirror bumps in `setup.py` (or `pyproject.toml`) `install_requires`
- [x] 1.3 Pin `apibackuper>=0.4.0` in requirements.txt and setup.py
- [x] 1.4 Regenerate `requirements-pinned.txt` with resolved current versions
- [x] 1.5 Audit `destinations/mongo.py` for pymongo 4.x API breaks (count→count_documents, etc.)
- [x] 1.6 Audit `sources/{xlsx,xls}.py` for pandas 2.x API breaks
- [x] 1.7 Update `DEPENDENCIES.md` with new pinning rationale

## 2. Tests
- [x] 2.1 Install with new deps in clean venv, run full pytest suite
- [x] 2.2 Add/extend test for MongoDB destination using mongomock or pytest-mock
- [x] 2.3 Verify xlsx/xls source tests pass with pandas 2.x

## 3. Verification
- [x] 3.1 `pip-audit` reports no known vulnerabilities for pinned set
- [x] 3.2 `pytest` green
- [x] 3.3 `openspec validate update-dependencies --strict`
