---
title: "Processor configuration"
description: "processor block: source type, keymap, typemap, custom code"
---

# Processor configuration

```yaml
processor:
  config:
    type: csv          # optional reader; inferred from extension when possible
    error_strategy: skip   # skip | fail | retry
    max_retries: 3
    autoid: true
    autotype: false
  keymap:
    type: names        # names | position
    fields:
      old: new
  typemap:
    amount: float
    when: datetime
  custom:
    type: script
    code: scripts/transform.py
```

## Source `config.type`

Registered readers include `csv`, `json`, `jsonl`, `xml`, `xls`, `xlsx`,
`bson`, `zipxml`. XML and ZIP+XML require `tagname`. Excel requires `keys`
(and usually `start_line`).

## Error handling

- `skip` — drop the record (written to `output/errors.jsonl`)
- `fail` — stop the pipeline
- `retry` — retry with backoff (`max_retries`)

## Custom code

`code` is a path relative to the project. The module must define
`process(record)` returning a dict. Scripts outside the project directory are
rejected.

Concepts: [Processors](/concepts/processors).
