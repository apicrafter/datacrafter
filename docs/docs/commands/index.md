---
title: "CLI Reference"
description: "All datacrafter commands"
---

# CLI Reference

The entry point is `datacrafter` (Typer). Global style: `--path` / `-p` selects
the project directory (default: current working directory). `--verbose` / `-v`
raises log level.

| Command | Purpose |
|---------|---------|
| [`init`](/commands/init) | Create a project directory and `datacrafter.yml` |
| [`run`](/commands/run) | Execute the pipeline (`--dry-run` prints a plan) |
| [`check`](/commands/check) | Validate config and environment |
| [`status`](/commands/status) | Latest `state.json` stages |
| [`log`](/commands/log) | Tail `datacrafter.log` |
| [`clean`](/commands/clean) | Remove temp files (`--storage` also clears storage) |
| [`schema`](/commands/schema) | Infer field types from output JSONL |
| [`metrics`](/commands/metrics) | Record counts and field histograms |
| [`config validate`](/commands/config) | Validate YAML only |
| [`config schema`](/commands/config) | Print expected configuration schema |
| [`version`](/commands/version) | Print package version |

## Planned (not implemented)

These commands exist as stubs and print that they are not implemented yet:

- `datacrafter builds` — manage builds
- `datacrafter push` — push to remote storage
- `datacrafter ui` — web UI
