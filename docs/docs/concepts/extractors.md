---
title: "Extractors"
description: "How Datacrafter pulls files and catalogs into current/"
---

# Extractors

Extractors download or generate files into `current/`. Configure one with
`extractor:` or several with `extractors:` (they share one processor and
destination).

**Modes** (`mode`) are `singlefile`, `api`, or `code`.

**File types** include `file-csv`, `file-json`, `file-jsonl`, `file-xml`,
`file-xls`, `file-xlsx`, and `file-zip`.

**Other types:** `api` (APIBackuper), `code` (trusted Python `collect()`),
`rss`, and `dcat`.

**Methods** for files are typically `url` or `urlbypattern`. APIBackuper uses
`method: apibackuper`.

Full YAML examples: [Extractor configuration](/configuration/extractors).

## File URL

```yaml
extractor:
  type: file-json
  method: url
  mode: singlefile
  config:
    url: https://example.com/data.json
```

## Patterned HTML index (`urlbypattern`)

```yaml
extractor:
  type: file-zip
  method: urlbypattern
  mode: singlefile
  config:
    prefix: https://www.nalog.ru/opendata/7707329152-taxoffence/
    data_prefix: https://data.nalog.ru/opendata/7707329152-taxoffence/data-
```

## Several extractors

```yaml
extractors:
  - name: feed
    type: rss
    config:
      url: https://example.com/feed.xml
  - name: catalog
    type: dcat
    config:
      url: https://example.com/catalog.json
```

After the extractor stage, `state.json` records filenames under `current/`.

Planned (not implemented): generic REST beyond URL download, CMS, FTP/SFTP,
and vendor analytics APIs.
