---
title: "schema"
description: "Infer field types from project JSONL output"
---

# schema

```bash
datacrafter schema [--path PATH]
```

Reads JSONL in `output/` (or `current/` if needed) and prints inferred field
types as YAML. Run the pipeline first if no JSONL files exist.

Related: [`metrics`](/commands/metrics) for counts and histograms.
