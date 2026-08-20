---
title: "status"
description: "Show the latest pipeline execution state"
---

# status

```bash
datacrafter status [--path PATH] [--verbose]
```

Reads `state.json` and prints each stage name and status (`success` / `fail`).
If the file is missing, run [`datacrafter run`](/commands/run) first.
