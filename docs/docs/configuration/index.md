---
title: "Configuration"
description: "datacrafter.yml schema"
---

# Configuration

Pipelines are declared in `datacrafter.yml`. Print the live schema (registered
types included) with:

```bash
datacrafter config schema
```

## Top-level keys

| Key | Required | Notes |
|-----|----------|--------|
| `version` | yes | `"1"` |
| `project-name` | yes | Human-readable name |
| `project-id` | recommended | Unique id from `init` |
| `extractor` or `extractors` | yes for `run` / `check` | See [extractors](/configuration/extractors) |
| `processor` | no | See [processors](/configuration/processors) |
| `destination` | no | See [destinations](/configuration/destinations) |

Environment interpolation: `${VAR}` and `${VAR:-default}` in string values.

## Example

```yaml
version: "1"
project-name: "my-project"
project-id: "unique-id"

extractor:
  mode: "singlefile"
  type: "file-csv"
  method: "url"
  force: true
  config:
    url: "https://example.com/data.csv"

processor:
  config:
    autoid: true
    autotype: false
    error_strategy: "skip"
    max_retries: 3
  keymap:
    type: "names"
    fields:
      old_name: "new_name"
  typemap:
    field_name: "int"
  custom:
    type: "script"
    code: "scripts/transform.py"

destination:
  type: "file-jsonl"
  fileprefix: "output"
  compress: "gz"
```

## Related

- [Extractor configuration](/configuration/extractors)
- [Processor configuration](/configuration/processors)
- [Destination configuration](/configuration/destinations)
- [Security](/configuration/security)
