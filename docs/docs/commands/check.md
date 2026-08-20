---
title: "check"
description: "Validate configuration and environment"
---

# check

```bash
datacrafter check [--path PATH] [--verbose]
```

Loads `datacrafter.yml`, runs the same validation as `run`, then checks that
optional destination drivers and related tools are available.

```bash
datacrafter check
datacrafter check --path examples/zip-xml
```

For YAML-only validation without environment checks, use
[`datacrafter config validate`](/commands/config).
