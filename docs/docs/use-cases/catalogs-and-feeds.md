---
title: "Catalogs and feeds"
description: "RSS/Atom, DCAT catalogs, and APIBackuper exports"
---

# Catalogs and feeds

## RSS / Atom

```yaml
extractor:
  type: rss
  config:
    url: https://example.com/feed.xml
    download_enclosures: false
```

Recipe: [`examples/rss-feed/`](https://github.com/apicrafter/datacrafter/tree/main/examples/rss-feed).
Set `download_enclosures: true` to fetch enclosure files.

## DCAT JSON catalog

```yaml
extractor:
  type: dcat
  config:
    url: https://example.com/catalog.json
```

The in-tree DCAT example also shows compressed JSONL output
(`compression: zst`). See
[`examples/dcat/`](https://github.com/apicrafter/datacrafter/tree/main/examples/dcat).

## APIBackuper

Put `apibackuper.cfg` under `storage/` and use `mode: api` (not `full` —
validation rejects unknown modes):

```yaml
extractor:
  type: api
  method: apibackuper
  mode: api
```

Recipe: [`examples/apibackuper/`](https://github.com/apicrafter/datacrafter/tree/main/examples/apibackuper).
Requires the `apibackuper` CLI on `PATH`.

## Several sources, one processor

Use `extractors:` as a list. Each entry can have a `name`. They share the
project processor and destination.
