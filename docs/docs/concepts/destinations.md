---
title: "Destinations"
description: "Where processed records are written"
---

# Destinations

Destinations receive transformed records. Types:

**Files:** `file-jsonl`, `file-bson`, `file-csv`, `file-parquet` (needs pyarrow).

**Stores:** `mongodb`, `arangodb`, `couchdb`, `meilisearch`.

File names are `fileprefix` plus the type extension. Optional compression:
`xz`, `gz`, `bz2`, `zip`, `zst` (both `compress` and `compression` keys work;
`zst` needs the `compression` extra).

```yaml
destination:
  type: file-bson
  compress: xz
  fileprefix: fnspaytax
```

File destinations also write `output/datapackage.json` (Frictionless Data
Package) next to the data file.

MongoDB example:

```yaml
destination:
  type: mongodb
  connstr: "${MONGO_URI}"
  dbname: mydb
  tablename: mydata
```

YAML details: [Destination configuration](/configuration/destinations).

Planned (not implemented): JSON/YAML file destinations, ClickHouse / SQLAlchemy,
and remote storage (S3, FTP, WebDAV).
