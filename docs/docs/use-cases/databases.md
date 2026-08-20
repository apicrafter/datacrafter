---
title: "Document stores"
description: "Load processed records into MongoDB, ArangoDB, CouchDB, or Meilisearch"
---

# Document stores

After mapping records, write them to a document database or search index.
Install the matching Python driver first; [`datacrafter check`](/commands/check)
reports missing packages.

```yaml
destination:
  type: mongodb
  connstr: "${MONGO_URI}"
  dbname: mydb
  tablename: mydata
```

| Type | Typical keys | Package |
|------|----------------|---------|
| `mongodb` | `connstr`, `dbname`, `tablename` | `pymongo` |
| `arangodb` | `connstr`, `dbname`, `tablename` | `python-arango` |
| `couchdb` | `connstr`, `dbname` | `pycouchdb` |
| `meilisearch` | host / API key fields used by the destination | `meilisearch` |

Keep secrets in the environment. See [Security](/configuration/security).

For a file that MongoDB tools can ingest without a live server, use
`type: file-bson` instead.
