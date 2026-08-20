---
title: "Processors"
description: "Record transforms: keymap, typemap, autotype, autoid, custom code"
---

# Processors

The processor reads files from `current/`, yields records, applies steps, and
writes to the destination. `processor.config.type` selects the source reader
when it is not obvious from the file extension (`zipxml`, `xlsx`, `csv`, …).

## Steps

| Step | What it does |
|------|----------------|
| `keymap` | Rename fields (`type: names`) or assign names by position |
| `typemap` | Convert values (`int`, `float`, `date`, `datetime`, `bool`) |
| `autotype` | Infer int/float/bool/date from a record sample |
| `autoid` | Write a stable `_id` (opt-in; default is off) |
| `custom` | Python `process(record)` in a project-local script |

`error_strategy` is `skip`, `fail`, or `retry`. Failed or skipped records go to
`output/errors.jsonl`.

Example ZIP+XML with keymap and typemap:

```yaml
processor:
  config:
    type: zipxml
    tagname: Документ
  keymap:
    type: names
    fields:
      НаимОрг: orgname
      ИННЮЛ: inn
  typemap:
    date_formed: datetime
    date_doc: datetime
```

Excel with headers and a custom cleaner:

```yaml
processor:
  config:
    start_line: 1
    autoid: true
    autotype: true
    keys: territory,years,id,kpp,fullname
  custom:
    type: script
    code: scripts/cleaner.py
```

```python
def process(r):
    r['years'] = r['years'].split()
    return r
```

The script must resolve **inside the project directory**. See
[Security](/configuration/security).

YAML details: [Processor configuration](/configuration/processors).
