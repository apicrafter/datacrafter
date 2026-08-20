---
title: "ZIP+XML open data"
description: "Unpack ZIP archives of XML records with tagname and keymap"
---

# ZIP+XML open data

Government dumps are often a ZIP of XML files with a repeating element.
Set processor `type: zipxml` and `tagname`. Recipe:
[`examples/zip-xml/`](https://github.com/apicrafter/datacrafter/tree/main/examples/zip-xml).

```yaml
version: "1"
project-name: zip-xml
project-id: example-zip-xml

extractor:
  mode: singlefile
  type: file-zip
  method: url
  force: true
  config:
    url: https://example.com/dump.zip

processor:
  config:
    type: zipxml
    tagname: item
    autotype: true
    error_strategy: skip
  keymap:
    type: names
    fields:
      НаимОрг: orgname
      ИННЮЛ: inn

destination:
  type: file-jsonl
  fileprefix: items
```

If the ZIP URL is only listed on an HTML index, use `method: urlbypattern`
with `prefix` and `data_prefix` instead of a direct `url`.

Do not treat the ZIP as stream compression. `gz` / `bz2` / `xz` / `zst` wrap a
single file; `zipxml` opens the archive path.
