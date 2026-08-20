---
title: "CSV to JSONL"
description: "Extract a CSV URL and write JSON Lines with autotype"
---

# CSV to JSONL

Package a remote CSV as JSON Lines. The in-repo recipe is
[`examples/csv-url/`](https://github.com/apicrafter/datacrafter/tree/main/examples/csv-url).

```yaml
version: "1"
project-name: csv-url
project-id: example-csv-url

extractor:
  mode: singlefile
  type: file-csv
  method: url
  force: true
  config:
    url: https://example.com/data.csv

processor:
  config:
    autotype: true
    autoid: true
    error_strategy: skip

destination:
  type: file-jsonl
  fileprefix: output
```

```bash
datacrafter check --path examples/csv-url
datacrafter run --dry-run --path examples/csv-url
```

Replace the placeholder URL, then `datacrafter run`. Inspect types with
[`datacrafter schema`](/commands/schema). Output includes `output/datapackage.json`.
