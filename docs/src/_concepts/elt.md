---
title: "What is NoSQL ETL?"
description: "How Datacrafter extracts, transforms, and loads record-oriented data"
layout: doc
weight: 11
---

Datacrafter is an **ETL** (Extract, Transform, Load) command-line tool. It is
built for record-oriented, NoSQL-shaped data — JSON Lines and BSON — not for
warehouse SQL transforms.

## Extract, Transform, Load

1. **Extract** — download or generate files into `current/` (URL, patterned HTML
   index, APIBackuper, RSS/Atom, DCAT catalog, or a trusted Python `collect()` script).
2. **Transform** — iterate records through `keymap`, `typemap`, optional
   `autotype` / `autoid`, and optional custom Python `process(record)`.
3. **Load** — write JSONL/BSON/CSV/Parquet (optionally compressed) or a document
   store / search index (MongoDB, ArangoDB, CouchDB, Meilisearch). File destinations
   also write `output/datapackage.json` unless disabled.

That is the opposite of **ELT** (load first, transform in the warehouse).
Datacrafter shapes records **before** they are written to the destination.

## When to use Datacrafter

- Packaging public or government dumps (CSV, Excel, ZIP+XML, RSS/Atom, DCAT catalogs)
- Repeating the same extract → JSONL/BSON job from a git-friendly `datacrafter.yml`
- Loading cleaned documents into MongoDB, ArangoDB, CouchDB, or Meilisearch

Datacrafter is not a warehouse orchestrator, a dbt replacement, or a Meltano /
Singer tap catalog. Those tools solve different problems.

## Project layout

A Datacrafter project is a directory, not a hidden SQLite database:

```
my-project/
├── datacrafter.yml
├── current/          # extracted files
├── output/           # processor output
├── temp/
├── storage/
├── state.json
└── datacrafter.log
```
