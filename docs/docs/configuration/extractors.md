---
title: "Extractor configuration"
description: "extractor and extractors keys in datacrafter.yml"
---

# Extractor configuration

Use `extractor:` for one source or `extractors:` for a list. Each spec needs
`type`. File extractors typically set `mode` and `method`.

## Modes

`singlefile`, `api`, `code`. Unknown modes fail validation.

## File types

`file-csv`, `file-json`, `file-jsonl`, `file-xml`, `file-xls`, `file-xlsx`,
`file-zip`.

Methods: `url` (needs `config.url`), `urlbypattern` (needs `prefix` and
`data_prefix`).

`force: true` re-downloads into `current/`.

## APIBackuper

```yaml
extractor:
  type: api
  method: apibackuper
  mode: api
```

Keep `apibackuper.cfg` under `storage/`.

## Code extractor

```yaml
extractor:
  type: code
  mode: code
  config:
    script: scripts/collect.py
```

The script must live under the project directory and expose `collect()`. It is
**trusted** input. See [Security](/configuration/security).

## RSS and DCAT

```yaml
extractors:
  - name: feed
    type: rss
    config:
      url: https://example.com/feed.xml
      download_enclosures: false   # true: fetch enclosure files into current/
  - name: catalog
    type: dcat
    config:
      url: https://example.com/catalog.json
      download: false              # true: fetch distribution files
      format: csv                  # only distributions matching this format
```

## Download options

URL downloads accept optional keys in `config` (they apply to `url`,
`urlbypattern`, and feed/catalog downloads):

```yaml
config:
  url: https://example.com/data.csv
  timeout: 60          # request timeout in seconds (default: 30)
  verify_tls: false    # only for trusted endpoints; logs a warning
  # aria2: true        # hand the download to aria2 (invoked without a shell)
  # aria2path: aria2c  # explicit aria2 binary path
```

TLS verification is on by default. See [Security](/configuration/security).

Concepts: [Extractors](/concepts/extractors).
