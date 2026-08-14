# In-repo pipeline recipes

Copy a directory, edit the placeholder URL, then run:

```bash
datacrafter check --path examples/csv-url
datacrafter run --dry-run --path examples/csv-url
```

| Recipe | What it shows |
|---|---|
| `csv-url/` | Single CSV URL → JSONL with autotype and autoid |
| `xlsx-registry/` | Excel file with `keys` / `start_line` |
| `zip-xml/` | ZIP+XML via `tagname` |
| `apibackuper/` | APIBackuper export → JSONL (`storage/apibackuper.cfg` required) |
| `rss-feed/` | RSS/Atom catalog → JSONL |
| `dcat/` | DCAT JSON catalog → compressed JSONL |

Additional recipes live at https://github.com/apicrafter/datacrafter-examples
