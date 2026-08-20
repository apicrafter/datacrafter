---
title: "config"
description: "Validate YAML and print the configuration schema"
---

# config

## `config validate`

```bash
datacrafter config validate [--path PATH] [--verbose]
```

Validates `datacrafter.yml` without running extractors. Does not check optional
Python drivers; use [`check`](/commands/check) for that.

## `config schema`

```bash
datacrafter config schema
```

Prints the expected configuration file shape, including registered extractor
and destination types from the plugin registry.

See [Configuration](/configuration/).
