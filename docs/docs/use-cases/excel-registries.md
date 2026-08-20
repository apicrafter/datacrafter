---
title: "Excel registries"
description: "Read XLSX sheets with header keys and start_line"
---

# Excel registries

Many public registries are Excel workbooks. Set `keys` to the header names and
`start_line` so rows become dicts. Recipe:
[`examples/xlsx-registry/`](https://github.com/apicrafter/datacrafter/tree/main/examples/xlsx-registry).

```yaml
version: "1"
project-name: xlsx-registry
project-id: example-xlsx-registry

extractor:
  mode: singlefile
  type: file-xlsx
  method: url
  force: true
  config:
    url: https://example.com/registry.xlsx

processor:
  config:
    type: xlsx
    start_line: 1
    keys: id,name,region
    autotype: true
    error_strategy: skip

destination:
  type: file-jsonl
  fileprefix: registry
```

Sheet selection uses `page` / `start_page` when you need a worksheet other than
the active one. `.xls` files use `type: file-xls` on the extractor and
`type: xls` on the processor.
