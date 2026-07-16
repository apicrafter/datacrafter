# Change: Update Outdated & Vulnerable Dependencies

## Why
`requirements-pinned.txt` pins years-old versions with known CVEs and Python 3.11+
incompatibilities: `pymongo==3.11.0` (3.x EOL, CVEs; current 4.x), `requests==2.28.0`
(CVE-2023-32681 fixed in 2.31.0), `lxml==4.9.0` (CVEs fixed in 4.9.1+), `pandas==1.1.3`
(2020; will not install on Python 3.11+), `chardet==3.0.4` (2017). Additionally
`apibackuper` is unpinned in both `requirements.txt` and `setup.py` (every other dep
has a lower bound). `pip-audit` is a declared dev dependency but never run in CI.

## What Changes
- Raise the lower bounds in `requirements.txt` and `setup.py` `install_requires`:
  `pymongo>=4.6.0`, `requests>=2.31.0`, `lxml>=4.9.1`, `pandas>=2.0.0`,
  `chardet>=5.0.0`, `beautifulsoup4>=4.12.0`, `pyyaml>=6.0.1`.
- Pin `apibackuper>=0.4.0` (verify latest available) in both `requirements.txt` and
  `setup.py`.
- Regenerate `requirements-pinned.txt` against the new floors using current versions.
- Update `DEPENDENCIES.md` to document the new pinning strategy.
- Validate pymongo 4.x migration (API changes: `insert_one`/`insert_many` unchanged,
  but `count` removed → `count_documents`; check `destinations/mongo.py`).

## Impact
- Affected specs: `dependencies`
- Affected code: `requirements.txt`, `requirements-pinned.txt`, `setup.py`/
  `pyproject.toml`, `DEPENDENCIES.md`, possibly `destinations/mongo.py`
- Risk: medium — pymongo 3→4 and pandas 1→2 have API breaks; must verify destinations
  and run tests. Pandas is only used by xlsx/xls sources.
