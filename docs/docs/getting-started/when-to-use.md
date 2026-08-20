---
title: "When to use Datacrafter"
description: "Datacrafter vs dbt, Meltano, Airbyte, and undatum"
---

# When to use Datacrafter

Datacrafter is a **CLI-first ETL tool for record-oriented, NoSQL-shaped data**.
Pipelines are declared in `datacrafter.yml`, extracted files land in `current/`,
and records are mapped **before** they are written to JSONL, BSON, CSV, Parquet,
or a document store.

| Need | Prefer |
|------|--------|
| Repeatable extract → JSONL/BSON from public dumps (CSV, Excel, ZIP+XML, RSS, DCAT) | **Datacrafter** |
| Load cleaned documents into MongoDB, ArangoDB, CouchDB, or Meilisearch | **Datacrafter** |
| Warehouse SQL transforms, models, and tests | **dbt** |
| Singer/Meltano tap catalogs and ELT into a warehouse | **Meltano** / **Airbyte** |
| Convert, validate, and query files without a YAML project | **[undatum](https://github.com/datenoio/undatum)** |
| Ad-hoc SQL on Parquet/CSV | **DuckDB** |

## Datacrafter strengths

- Git-friendly project directory, not a hidden SQLite system database
- File and URL extractors plus APIBackuper, RSS/Atom, and DCAT catalogs
- Record transforms: `keymap`, `typemap`, `autotype`, `autoid`, custom Python
- Native intermediate formats: JSON Lines and BSON
- `datapackage.json` beside file output; `${VAR}` interpolation in YAML

## When another tool wins

- **dbt**: you already model in SQL inside a warehouse
- **Meltano / Airbyte**: you need a large tap catalog and ELT (load first)
- **undatum**: one-off convert/validate/SQL on files, no pipeline project
- **Airflow / Dagster**: multi-team orchestration across many systems

Datacrafter is not a warehouse orchestrator and does not implement Meltano
plugins or Singer taps.

## Related docs

- [Quick start](/getting-started/quick-start)
- [What is NoSQL ETL?](/concepts/etl)
- [Cookbook](/getting-started/cookbook)
