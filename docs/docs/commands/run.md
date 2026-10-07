---
title: "run"
description: "Execute the extract → process → load pipeline"
---

# run

```bash
datacrafter run [--path PATH] [--verbose] [--quiet] [--dry-run]
                [--skip-validation] [--structured-log]
```

Validates `datacrafter.yml` (unless `--skip-validation`), then runs extractors,
the processor, and the destination.

| Flag | Effect |
|------|--------|
| `--dry-run` | Validate and print a YAML plan; do not download or write |
| `--verbose` / `-v` | Debug logging |
| `--quiet` / `-q` | Errors only |
| `--structured-log` | JSON log records |
| `--path` / `-p` | Project directory |

`--dry-run` lists every `extractors:` entry (and keeps singular `extractor` as
the first spec).

If writing or finalizing the destination fails (for example a flush error on
close), the run exits non-zero and `state.json` records the failed
`destination` stage with the error text.

```bash
datacrafter run -v
datacrafter run --dry-run --path examples/csv-url
```
