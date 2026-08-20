---
title: "Installation"
description: "Install Datacrafter with pip or from source"
---

# Installation

Datacrafter requires **Python 3.9 or newer**.

## Using pip (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install datacrafter
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

| Destination | Package |
|-------------|----------|
| `file-parquet` | `pip install "datacrafter[parquet]"` (pyarrow) |
| `mongodb` | `pymongo` |
| `arangodb` | `python-arango` |
| `couchdb` | `pycouchdb` |
| `meilisearch` | `meilisearch` |

APIBackuper extractors also need the `apibackuper` CLI (`>=1.0.4`) on `PATH`.

`datacrafter check` reports missing optional packages for the destination you
configured.

## Requirements

- Python 3.9 or greater (CI tests 3.9–3.13)
- A writable project directory for `current/`, `output/`, and `state.json`

## Next steps

- [Quick start](/getting-started/quick-start)
- [When to use Datacrafter](/getting-started/when-to-use)
- [Configuration schema](/configuration/)
