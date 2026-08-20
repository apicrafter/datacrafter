---
title: "Troubleshooting"
description: "Common Datacrafter errors and how to fix them"
---

# Troubleshooting

## Configuration validation failed

`datacrafter run` and `datacrafter check` call `validate_config` before work
starts.

- Missing `version` or `project-name`
- No `extractor` / `extractors` block
- Unknown extractor, source, or destination `type` (the error lists registered names)
- Unknown extractor `mode` (must be `singlefile`, `api`, or `code`)
- Unknown `method` for file extractors (`url`, `urlbypattern`, `apibackuper`)

Print the expected schema:

```bash
datacrafter config schema
datacrafter config validate
```

## Project configuration file not found

Run commands from a directory that contains `datacrafter.yml`, or pass
`--path`:

```bash
datacrafter check --path ./my-project
```

Create a project with [`datacrafter init`](/commands/init) if the file is missing.

## Environment issues after a valid config

`datacrafter check` then looks for optional drivers. Install the matching
package (`pymongo`, `python-arango`, `pycouchdb`, `meilisearch`, `pyarrow`)
or change the destination type.

APIBackuper extractors need the `apibackuper` tool on `PATH` and
`storage/apibackuper.cfg` in the project.

## No JSONL files for schema or metrics

[`datacrafter schema`](/commands/schema) and [`metrics`](/commands/metrics)
read JSONL under `output/` (or `current/`). Run the pipeline first, or point
`--path` at a project that already has output.

## Extractor downloaded nothing

- Confirm the URL returns the file (TLS is verified by default)
- For `urlbypattern`, both `prefix` and `data_prefix` must match the HTML index
- `force: true` re-downloads even if `current/` already has a file

## Processor skipped or failed records

`error_strategy` is `skip`, `fail`, or `retry`. Skipped or failed records go to
`output/errors.jsonl`. Custom scripts must define `process(record)` and live
**inside the project directory**.

## ZIP treated as a stream

If the source is a ZIP of XML files, set processor `config.type: zipxml` and
`tagname` to the repeating element. A `.zip` archive is not stream compression
(`gz` / `bz2` / `xz` / `zst`).

## Secrets in YAML

Use environment interpolation instead of committing credentials:

```yaml
connstr: "${MONGO_URI}"
# or
connstr: "${MONGO_URI:-mongodb://localhost:27017}"
```

See [Security](/configuration/security).

## Related documentation

- [Installation](/getting-started/installation)
- [Configuration](/configuration/)
- [CLI reference](/commands/)
