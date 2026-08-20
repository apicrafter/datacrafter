---
title: "Quick Start"
description: "Task-oriented first success paths for Datacrafter"
---

# Quick Start

Short paths to a first pipeline. New to Datacrafter? Pick a role in the
[cookbook](/getting-started/cookbook) after this page.

## CSV URL → JSONL in a minute

```bash
pip install datacrafter
datacrafter init my-project
cd my-project
```

Edit `datacrafter.yml`:

```yaml
version: "1"
project-name: "my-project"
project-id: "unique-id"

extractor:
  mode: "singlefile"
  type: "file-csv"
  method: "url"
  config:
    url: "https://example.com/data.csv"

processor:
  config:
    autotype: true
    autoid: true
    error_strategy: "skip"

destination:
  type: "file-jsonl"
  fileprefix: "output"
```

Then validate and run:

```bash
datacrafter check
datacrafter run --dry-run
datacrafter run
datacrafter schema
```

Extracted files land in `current/`. Processed output is in `output/` (plus
`datapackage.json` for file destinations). `state.json` records stage status.

In-repo recipes live under [`examples/`](https://github.com/apicrafter/datacrafter/tree/main/examples)
in the repository. Copy one and change the URL:

```bash
datacrafter check --path examples/csv-url
datacrafter run --dry-run --path examples/csv-url
```

## Inspect output after a run

```bash
datacrafter status
datacrafter schema
datacrafter metrics
datacrafter log -n 50
```

## Load into MongoDB

Set a connection string from the environment, not in git:

```yaml
destination:
  type: mongodb
  connstr: "${MONGO_URI}"
  dbname: mydb
  tablename: mydata
```

```bash
export MONGO_URI="mongodb://localhost:27017"
datacrafter check
datacrafter run
```

## Next steps

- [Cookbook](/getting-started/cookbook) — task-oriented index by role
- [Projects](/concepts/projects) — directory layout and `datacrafter.yml`
- [When to use Datacrafter](/getting-started/when-to-use)
- [Troubleshooting](/getting-started/troubleshooting)
