---
title: "Destination configuration"
description: "File and database destination keys"
---

# Destination configuration

```yaml
destination:
  type: file-jsonl     # see table
  fileprefix: output   # required for file-* types
  compress: gz         # optional: gz, bz2, xz, zip, zst
  storage: local
```

`compress` and `compression` are both accepted.

## File types

| Type | Extension | Extra package |
|------|-----------|----------------|
| `file-jsonl` | `.jsonl` | — |
| `file-bson` | `.bson` | — |
| `file-csv` | `.csv` | optional `delimiter` / `quotechar` |
| `file-parquet` | `.parquet` | `pyarrow` (`datacrafter[parquet]`) |

File destinations write `output/datapackage.json` beside the data file.

## Databases and search

```yaml
destination:
  type: mongodb
  connstr: "${MONGO_URI}"
  dbname: mydb
  tablename: mytable
```

| Type | Package |
|------|---------|
| `mongodb` | `pymongo` |
| `arangodb` | `python-arango` |
| `couchdb` | `pycouchdb` |
| `meilisearch` | `meilisearch` |

Concepts: [Destinations](/concepts/destinations).
