---
title: "Installation"
description: "Install Datacrafter with pip or from source"
---

# Installation

Datacrafter requires **Python 3.10 or newer**.

> The `datacrafter` name on PyPI belongs to an unrelated project; releases
> are distributed from GitHub.

## From a GitHub release (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install \
  https://github.com/apicrafter/datacrafter/releases/download/v2.0.0/datacrafter-2.0.0-py3-none-any.whl
datacrafter version
```

## From source

```bash
git clone https://github.com/apicrafter/datacrafter.git
cd datacrafter
pip install -e .
```

For tests and linters, install the development extras:

```bash
pip install -r requirements-dev.txt
pip install -e .
```

## Optional destinations

File JSONL, BSON, and CSV destinations ship with the core package. Some
destinations need extra Python packages:

| Destination / feature | Package |
|------------------------|----------|
| `file-parquet` | `pip install "datacrafter[parquet]"` (pyarrow) |
| `.zst` compression (sources and destinations) | `pip install "datacrafter[compression]"` (zstandard) |
| `mongodb` | `pymongo` |
| `arangodb` | `python-arango` |
| `couchdb` | `pycouchdb` |
| `meilisearch` | `meilisearch` |

APIBackuper extractors also need the `apibackuper` CLI (`>=1.0.4`) on `PATH`.

`datacrafter check` reports missing optional packages for the destination you
configured.

## Requirements

- Python 3.10 or greater (CI tests 3.10–3.13)
- A writable project directory for `current/`, `output/`, and `state.json`

## Next steps

- [Quick start](/getting-started/quick-start)
- [When to use Datacrafter](/getting-started/when-to-use)
- [Configuration schema](/configuration/)
